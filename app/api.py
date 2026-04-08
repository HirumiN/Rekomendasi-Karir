from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from . import models, schemas, crud, db, auth, calendar_service, rag_service, rag

router = APIRouter(prefix="/api", tags=["api"])

# Dependency
def get_db():
    yield from db.get_db()

# --- USERS ---
@router.get("/me", response_model=schemas.User)
async def get_current_user_api(
    user: models.User = Depends(auth.get_current_active_user)
):
    """Get current logged in user"""
    return user

@router.post("/manual-sync")
def manual_sync(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    calendar_service.resync_all_user_calendars(db, current_user)
    return {"message": "Sync triggered"}

@router.get("/users", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# --- SEMESTERS ---
@router.get("/semesters", response_model=List[schemas.Semester])
def read_semesters(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_semesters_by_user(db, current_user.id_user)

@router.post("/semesters", response_model=schemas.Semester)
def create_semester(
    semester: schemas.SemesterCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if semester.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_semester = crud.create_semester(db, semester)
    # Sync with Calendar
    calendar_service.create_semester_calendar(db, current_user, db_semester)
    return db_semester

@router.put("/semesters/{semester_id}", response_model=schemas.Semester)
def update_semester(
    semester_id: int, 
    semester_update: schemas.SemesterUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_semester = crud.get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    if db_semester.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    updated_semester = crud.update_semester(db, semester_id, semester_update)
    
    # Sync with Calendar (Rename)
    calendar_service.update_semester_calendar(db, current_user, updated_semester)
    # Ghost update for matkuls
    calendar_service.update_all_matkul_for_semester(db, current_user, updated_semester)
    
    return updated_semester

@router.delete("/semesters/{semester_id}")
def delete_semester(
    semester_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_semester = crud.get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    if db_semester.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Sync with Calendar (Delete)
    calendar_service.delete_semester_calendar(db, current_user, db_semester)
    
    crud.delete_semester(db, semester_id)
    return {"message": "Semester deleted"}

# --- JADWAL MATKUL ---
@router.get("/jadwal", response_model=List[schemas.JadwalMatkul])
def read_jadwal(
    semester_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if semester_id:
        return crud.get_jadwal_matkul_by_semester(db, semester_id)
    return crud.get_jadwal_matkul_by_user(db, current_user.id_user)

@router.post("/jadwal", response_model=schemas.JadwalMatkul)
async def create_jadwal(
    jadwal: schemas.JadwalMatkulCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if jadwal.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jadwal = crud.create_jadwal_matkul(db, jadwal)
    
    # Sync
    if jadwal.id_semester:
        db_semester = crud.get_semester(db, jadwal.id_semester)
        if db_semester:
            event_id = calendar_service.create_recurring_class_event(db, current_user, db_semester, db_jadwal)
            if event_id:
                db_jadwal.google_event_id = event_id
                db.commit()

    # Create Embedding
    await rag_service.update_jadwal_embedding(db, db_jadwal)

    return db_jadwal

@router.put("/jadwal/{jadwal_id}", response_model=schemas.JadwalMatkul)
async def update_jadwal(
    jadwal_id: int, 
    jadwal_update: schemas.JadwalMatkulUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_jadwal = crud.get_jadwal_matkul(db, jadwal_id)
    if not db_jadwal:
        raise HTTPException(status_code=404, detail="Jadwal not found")
    if db_jadwal.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    updated_jadwal = crud.update_jadwal_matkul(db, jadwal_id, jadwal_update)
    
    # Sync Update
    if updated_jadwal.id_semester and updated_jadwal.google_event_id:
        db_semester = crud.get_semester(db, updated_jadwal.id_semester)
        if db_semester:
             calendar_service.update_recurring_event(db, current_user, db_semester, updated_jadwal)

    # Update Embedding
    await rag_service.update_jadwal_embedding(db, updated_jadwal)

    return updated_jadwal

@router.delete("/jadwal/{jadwal_id}")
def delete_jadwal(
    jadwal_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_jadwal = crud.get_jadwal_matkul(db, jadwal_id)
    if not db_jadwal:
        raise HTTPException(status_code=404, detail="Jadwal not found")
    if db_jadwal.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Sync Delete
    if db_jadwal.google_event_id and db_jadwal.id_semester:
         db_semester = crud.get_semester(db, db_jadwal.id_semester)
         if db_semester and db_semester.google_calendar_id:
             calendar_service.delete_event(db, current_user, db_jadwal.google_event_id, calendar_id=db_semester.google_calendar_id)

    crud.delete_jadwal_matkul(db, jadwal_id)
    crud.delete_rags_embedding_by_source_type_and_id(db, "jadwal", str(jadwal_id))
    return {"message": "Jadwal deleted"}

# --- TODOS ---
@router.get("/todos", response_model=List[schemas.Todo])
def read_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.get_todos_by_user(db, current_user.id_user)

@router.post("/todos", response_model=schemas.Todo)
async def create_todo(
    todo: schemas.TodoCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if todo.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_todo = crud.create_todo(db, todo)
    
    # Sync
    if todo.tenggat:
        event_id = calendar_service.create_todo_event(db, current_user, db_todo)
        if event_id:
            db_todo.google_event_id = event_id
            db.commit()
            
    # Create Embedding
    await rag_service.update_todo_embedding(db, db_todo)

    return db_todo

@router.put("/todos/{todo_id}", response_model=schemas.Todo)
async def update_todo(
    todo_id: int, 
    todo_update: schemas.TodoUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_todo = crud.get_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if db_todo.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    updated_todo = crud.update_todo(db, todo_id, todo_update)
    
    # Update Sync
    if updated_todo:
         calendar_service.update_todo_event(db, current_user, updated_todo)
         db.commit() # Commit the potential google_event_id change if create happened inside update logic
         
         # Update Embedding
         await rag_service.update_todo_embedding(db, updated_todo)
    
    return updated_todo

@router.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_todo = crud.get_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if db_todo.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Sync Delete
    if db_todo.google_event_id:
        cal_id = current_user.todo_calendar_id if current_user.todo_calendar_id else 'primary'
        calendar_service.delete_event(db, current_user, db_todo.google_event_id, calendar_id=cal_id)

    crud.delete_todo(db, todo_id)
    crud.delete_rags_embedding_by_source_type_and_id(db, "todo", str(todo_id))
    return {"message": "Todo deleted"}

# --- RUTINITAS ---
@router.get("/rutinitas", response_model=List[schemas.Rutinitas])
def read_rutinitas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.get_rutinitas_by_user(db, current_user.id_user)

@router.post("/rutinitas", response_model=schemas.Rutinitas)
async def create_rutinitas(
    rutinitas: schemas.RutinitasCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if rutinitas.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_rutinitas = crud.create_rutinitas(db, rutinitas)
            
    await rag_service.update_rutinitas_embedding(db, db_rutinitas)
    return db_rutinitas

@router.put("/rutinitas/{rutinitas_id}", response_model=schemas.Rutinitas)
async def update_rutinitas(
    rutinitas_id: int, 
    rutinitas_update: schemas.RutinitasUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_rutinitas = crud.get_rutinitas(db, rutinitas_id)
    if not db_rutinitas:
        raise HTTPException(status_code=404, detail="Rutinitas not found")
    if db_rutinitas.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    updated_rutinitas = crud.update_rutinitas(db, rutinitas_id, rutinitas_update)
    
    if updated_rutinitas:
         await rag_service.update_rutinitas_embedding(db, updated_rutinitas)
    
    return updated_rutinitas

@router.delete("/rutinitas/{rutinitas_id}")
def delete_rutinitas(
    rutinitas_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_rutinitas = crud.get_rutinitas(db, rutinitas_id)
    if not db_rutinitas:
        raise HTTPException(status_code=404, detail="Rutinitas not found")
    if db_rutinitas.id_user != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    crud.delete_rutinitas(db, rutinitas_id)
    crud.delete_rags_embedding_by_source_type_and_id(db, "rutinitas", str(rutinitas_id))
    return {"message": "Rutinitas deleted"}

# --- ROADMAP ---
@router.get("/roadmaps", response_model=List[schemas.Roadmap])
def read_roadmaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.get_roadmaps_by_user(db, current_user.id_user)

@router.get("/roadmaps/{roadmap_id}/steps", response_model=List[schemas.RoadmapStep])
def read_roadmap_steps(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verify roadmap belongs to user
    roadmap = db.query(models.Roadmap).filter_by(id=roadmap_id, id_user=current_user.id_user).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return crud.get_roadmap_steps_by_roadmap(db, roadmap_id)

@router.get("/career-progress", response_model=List[schemas.CareerProgress])
def read_career_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.get_career_progress_by_user(db, current_user.id_user)

@router.put("/career-progress/{progress_id}", response_model=schemas.CareerProgress)
def update_career_progress(
    progress_id: int,
    progress_update: schemas.CareerProgressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verify ownership
    progress = db.query(models.CareerProgress).filter_by(id=progress_id, id_user=current_user.id_user).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return crud.update_career_progress(db, progress_id, progress_update)


# --- CAREER ANALYSIS ---
@router.post("/ai/career-analysis/generate")
async def generate_career_analysis_api(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if user_id != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Only Generate analysis (don't save yet)
    data = await rag.generate_career_analysis(db, user_id)

    return {
        "message": "Career analysis generated",
        "data": data
    }


from fastapi import Body

@router.post("/ai/career-analysis/save")
async def save_career_analysis_api(
    user_id: int, 
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if user_id != current_user.id_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Save Career Result
    careers_data = data.get("careers", [])
    primary_career_id = None
    career_name = "Kesuksesan Karir"
    
    if careers_data:
        career_name = careers_data[0].get("name", career_name)
        for c_idx, c_data in enumerate(careers_data):
            c_id = crud.save_career_result(db, user_id, {"career": c_data})
            if c_idx == 0:
                primary_career_id = c_id
    elif "career" in data:
        # Fallback to old format
        primary_career_id = crud.save_career_result(db, user_id, data)
        career_name = data.get("career", {}).get("name", "Career Analysis")
    else:
        raise HTTPException(status_code=400, detail="Invalid generation data format")

    # Insert Roadmap + Steps + Progress
    db_roadmap = crud.create_roadmap(db, schemas.RoadmapCreate(
        id_user=user_id,
        id_career=primary_career_id,
        title=f"Roadmap for {career_name}"
    ))

    step_global_order = 1
    if "roadmap" in data and isinstance(data["roadmap"], list):
        for phase_data in data["roadmap"]:
            phase_name = phase_data.get("phase", "")
            steps = phase_data.get("steps", [])
            for step in steps:
                db_step = crud.create_roadmap_step(db, schemas.RoadmapStepCreate(
                    id_roadmap=db_roadmap.id,
                    phase=phase_name,
                    step_order=step_global_order,
                    title=step.get("title", ""),
                    description=step.get("description", "")
                ))
                step_global_order += 1
                
                # Create Progress Tracker
                crud.create_career_progress(db, schemas.CareerProgressCreate(
                    id_user=user_id,
                    id_roadmap_step=db_step.id
                ))

    # Insert Tasks as Todos
    if "tasks" in data and isinstance(data["tasks"], list):
        for task in data["tasks"]:
            deadline_str = task.get("deadline", "")
            parsed_deadline = None
            if deadline_str:
                try:
                    parsed_deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                except ValueError:
                    pass

            db_todo = crud.create_todo(db, schemas.TodoCreate(
                id_user=user_id,
                nama=task.get("task", ""),
                tipe=task.get("priority", "Menengah"),
                tenggat=parsed_deadline,
                deskripsi=f"Dari Analisis Karir AI."
            ))
            
            # Sync to calendar
            if db_todo.tenggat:
                event_id = calendar_service.create_todo_event(db, current_user, db_todo)
                if event_id:
                    db_todo.google_event_id = event_id
                    db.commit()
            
            # Create Embedding
            await rag_service.update_todo_embedding(db, db_todo)

    return {
        "message": "Career analysis saved successfully to database"
    }
