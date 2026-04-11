from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from . import models, schemas, crud, db, auth, rag_service, rag

router = APIRouter(prefix="/api", tags=["api"])

from .db import get_db

# --- USERS ---
@router.get("/me", response_model=schemas.User)
async def get_current_user_api(
    user: models.User = Depends(auth.get_current_active_user)
):
    """Get current logged in user"""
    return user


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
    
    # Update Embedding
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

    crud.delete_jadwal_matkul(db, jadwal_id)

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

@router.delete("/roadmaps/{roadmap_id}", response_model=dict)
def delete_roadmap_endpoint(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    roadmap = db.query(models.Roadmap).filter_by(id=roadmap_id, id_user=current_user.id_user).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    crud.delete_roadmap(db, roadmap_id)
    return {"message": "Roadmap deleted successfully"}

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

    # ONE ROADMAP PER USER: Delete old roadmap data
    # This ensures a fresh start whenever a new career is chosen
    db.query(models.Roadmap).filter_by(id_user=user_id).delete()
    db.query(models.CareerResult).filter_by(id_user=user_id).delete()
    # DELETE old AI-generated tasks to ensure clean overwrite
    db.query(models.Todo).filter(
        models.Todo.id_user == user_id, 
        models.Todo.deskripsi == "Dari Analisis Karir AI."
    ).delete()
    
    # We don't commit here yet to maintain atomicity

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
                import json as _json
                skill_tags_raw = step.get("skill_tags")
                if isinstance(skill_tags_raw, list):
                    skill_tags_raw = _json.dumps(skill_tags_raw)
                db_step = crud.create_roadmap_step(db, schemas.RoadmapStepCreate(
                    id_roadmap=db_roadmap.id,
                    phase=phase_name,
                    step_order=step_global_order,
                    title=step.get("title", ""),
                    description=step.get("description", ""),
                    skill_tags=skill_tags_raw,
                    xp_reward=step.get("xp_reward", 10)
                ))
                step_global_order += 1
                
                # Create Progress Tracker
                crud.create_career_progress(db, schemas.CareerProgressCreate(
                    id_user=user_id,
                    id_roadmap_step=db_step.id
                ))

    # 4. Insert Tasks as Todos
    todo_embedding_tasks = []
    if "tasks" in data and isinstance(data["tasks"], list):
        for task in data["tasks"]:
            deadline_str = task.get("deadline", "")
            parsed_deadline = None
            if deadline_str:
                try:
                    parsed_deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                except ValueError:
                    try:
                        from datetime import date as _date
                        d = _date.fromisoformat(deadline_str[:10])
                        parsed_deadline = datetime(d.year, d.month, d.day)
                    except Exception:
                        pass

            db_todo = crud.create_todo(db, schemas.TodoCreate(
                id_user=user_id,
                nama=task.get("task", ""),
                tipe=task.get("priority", "Menengah"),
                tenggat=parsed_deadline,
                deskripsi=f"Dari Analisis Karir AI."
            ))
            
            # Collect for parallel embedding generation
            todo_embedding_tasks.append(rag_service.update_todo_embedding(db, db_todo, commit=False))

    # Perform all embeddings in parallel to speed up save
    if todo_embedding_tasks:
        import asyncio
        await asyncio.gather(*todo_embedding_tasks)

    # FINAL COMMIT for atomicity
    db.commit()

    return {
        "message": "Career analysis saved successfully to database"
    }


# ===================================================
# ROADMAP STEPS — Edit / Add / Delete / Complete
# ===================================================

@router.patch("/roadmap/steps/{step_id}", response_model=dict)
def edit_roadmap_step(
    step_id: int,
    update: schemas.RoadmapStepUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    step = db.query(models.RoadmapStep).join(models.Roadmap).filter(
        models.RoadmapStep.id == step_id,
        models.Roadmap.id_user == current_user.id_user
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    for field, value in update.model_dump(exclude_none=True).items():
        setattr(step, field, value)
    db.commit()
    db.refresh(step)
    return {"message": "Step updated", "step_id": step.id}


@router.post("/roadmap/steps", response_model=dict)
def add_roadmap_step(
    data: schemas.RoadmapStepCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    roadmap = db.query(models.Roadmap).filter_by(id=data.id_roadmap, id_user=current_user.id_user).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found or not authorized")

    step = models.RoadmapStep(
        id_roadmap=data.id_roadmap,
        phase=data.phase,
        step_order=data.step_order,
        title=data.title,
        description=data.description,
        skill_tags=data.skill_tags,
        xp_reward=data.xp_reward
    )
    db.add(step)
    db.commit()
    db.refresh(step)

    # Create progress tracker
    progress = models.CareerProgress(id_user=current_user.id_user, id_roadmap_step=step.id)
    db.add(progress)
    db.commit()

    return {"message": "Step added", "step_id": step.id}


@router.delete("/roadmap/steps/{step_id}")
def delete_roadmap_step(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    step = db.query(models.RoadmapStep).join(models.Roadmap).filter(
        models.RoadmapStep.id == step_id,
        models.Roadmap.id_user == current_user.id_user
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    db.delete(step)
    db.commit()
    return {"message": "Step deleted"}


@router.patch("/roadmap/steps/{step_id}/complete", response_model=schemas.XPGrantResponse)
def complete_roadmap_step(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    import json

    step = db.query(models.RoadmapStep).join(models.Roadmap).filter(
        models.RoadmapStep.id == step_id,
        models.Roadmap.id_user == current_user.id_user
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    # Mark progress as complete
    progress = db.query(models.CareerProgress).filter_by(
        id_roadmap_step=step_id, id_user=current_user.id_user
    ).first()
    if progress:
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()
        db.commit()

    # Grant XP per skill tag
    skills_raw = step.skill_tags or "[]"
    try:
        skill_list = json.loads(skills_raw)
    except Exception:
        skill_list = []

    xp_per_skill = step.xp_reward or 10
    updated_skills = []

    for skill in skill_list:
        existing = db.query(models.UserSkillXP).filter_by(
            id_user=current_user.id_user, skill_name=skill
        ).first()
        if existing:
            existing.xp_points += xp_per_skill
            existing.level = 1 + (existing.xp_points // 100)
        else:
            existing = models.UserSkillXP(
                id_user=current_user.id_user,
                skill_name=skill,
                xp_points=xp_per_skill,
                level=1
            )
            db.add(existing)
        db.commit()
        db.refresh(existing)
        updated_skills.append(existing)

    # Check if Phase is completed
    phase_completed = False
    all_steps_in_phase = db.query(models.RoadmapStep).filter_by(
        id_roadmap=step.id_roadmap, phase=step.phase
    ).all()
    
    step_ids = [s.id for s in all_steps_in_phase]
    completed_progress = db.query(models.CareerProgress).filter(
        models.CareerProgress.id_roadmap_step.in_(step_ids),
        models.CareerProgress.id_user == current_user.id_user,
        models.CareerProgress.status == "completed"
    ).all()
    
    if len(completed_progress) == len(all_steps_in_phase):
        phase_completed = True
        # Profile string refresh will pick up all skills including ones from this phase
        refresh_user_keterampilan_string(db, current_user)

    return schemas.XPGrantResponse(
        message=f"Step completed!{ ' Fase Selesai & Profil diperbarui!' if phase_completed else '' }",
        xp_granted=xp_per_skill,
        skills_updated=[schemas.SkillXPResponse.model_validate(s) for s in updated_skills],
        profile_updated=phase_completed
    )



@router.post("/profile/sync-skills", response_model=schemas.XPGrantResponse)
def sync_profile_skills(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    profile_updated = refresh_user_keterampilan_string(db, current_user)
        
    return schemas.XPGrantResponse(
        message="Profil berhasil disinkronkan dengan level terbaru!" if profile_updated else "Profil sudah sesuai dengan progres terbaru.",
        xp_granted=0,
        skills_updated=[],
        profile_updated=profile_updated
    )

def refresh_user_keterampilan_string(db: Session, user: models.User):
    """Rebuilds User.keterampilan based on actual UserSkillXP levels"""
    # 1. Get all earned XP for this user
    user_skills_earned = db.query(models.UserSkillXP).filter_by(id_user=user.id_user).all()
    
    # 2. Get current baseline from profile
    baseline_skills = parse_skill_string(user.keterampilan)
    
    # 3. Merge and update levels
    final_skills = {}
    
    # Use baseline first
    for name, xp in baseline_skills.items():
        level_name, _, _, _ = get_level_info(xp)
        final_skills[name] = level_name
        
    # Overwrite/Update with actual earned XP
    for s_xp in user_skills_earned:
        level_name, _, _, _ = get_level_info(s_xp.xp_points)
        final_skills[s_xp.skill_name] = level_name
        
    if not final_skills:
        return False

    # 4. Rebuild the keterampilan string: "Skill A (Level), Skill B (Level)"
    skill_parts = [f"{name} ({level})" for name, level in final_skills.items()]
    new_keterampilan = ", ".join(skill_parts)
    
    if new_keterampilan != user.keterampilan:
        user.keterampilan = new_keterampilan
        db.commit()
        db.refresh(user)
        return True
    return False


# ===================================================
# SKILL GAP
# ===================================================

def parse_skill_string(s: Optional[str]) -> dict:
    """Parses 'Skill (Level), Skill (Level)' into {Name: BaselineXP}"""
    # New thresholds: Pemula (0), Menengah (101), Mahir (301)
    level_map = {"Pemula": 20, "Menengah": 120, "Lanjutan": 320, "Mahir": 320}
    result = {}
    if not s: return result
    parts = [p.strip() for p in s.split(",")]
    for p in parts:
        if "(" in p and ")" in p:
            try:
                name = p.split("(")[0].strip()
                level = p.split("(")[1].split(")")[0].strip()
                result[name] = level_map.get(level, 0)
            except Exception:
                pass
        else:
            result[p] = 0
    return result

def get_level_info(xp: int):
    """Returns (current_level_name, next_level_name, progress_pct_in_level, next_level_xp)"""
    THRESHOLDS = [
        (0, 100, "Pemula", "Menengah"),
        (101, 300, "Menengah", "Mahir"),
        (301, 600, "Mahir", "Expert"),
        (601, 1000, "Expert", "Master"),
        (1001, 999999, "Master", "Legend")
    ]
    for min_xp, max_xp, current_name, next_name in THRESHOLDS:
        if xp <= max_xp:
            range_total = max_xp - min_xp + 1
            progress = ((xp - min_xp) / range_total) * 100
            return current_name, next_name, round(progress, 1), max_xp + 1
    return "Legend", "Ultimate", 100.0, 999999

@router.get("/skill-gap", response_model=schemas.SkillGapResponse)
def get_skill_gap(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # 1. Earned XP from Database
    user_skills_earned = db.query(models.UserSkillXP).filter_by(id_user=current_user.id_user).all()
    earned_xp_map = {s.skill_name: s for s in user_skills_earned}

    # 2. Baseline XP from Onboarding Preference
    pref_xp_map = parse_skill_string(current_user.keterampilan)

    # 3. Roadmap Context (to see what skills are in play)
    steps = db.query(models.RoadmapStep).join(models.Roadmap).filter(
        models.Roadmap.id_user == current_user.id_user
    ).all()

    import json
    roadmap_skills = set()
    for step in steps:
        try:
            tags = json.loads(step.skill_tags or "[]")
            for t in tags: roadmap_skills.add(t)
        except Exception: pass

    # 4. Merge all unique skills
    all_skill_names = set(earned_xp_map.keys()) | set(pref_xp_map.keys()) | roadmap_skills

    items = []
    for skill in all_skill_names:
        earned = earned_xp_map.get(skill)
        actual_earned_xp = earned.xp_points if earned else 0
        baseline_xp = pref_xp_map.get(skill, 0)
        
        current_xp = max(actual_earned_xp, baseline_xp)
        
        # New Leveling Logic
        level_name, next_level_name, progress_pct, next_xp_threshold = get_level_info(current_xp)
        
        # Calculate needed steps based on current level vs next
        xp_to_next = next_xp_threshold - current_xp
        needed_steps = max(1, int(xp_to_next / 20)) # Assuming 20 XP per step

        items.append(schemas.SkillGapItem(
            skill=skill,
            current_xp=current_xp,
            level_name=level_name,
            next_level_name=next_level_name,
            progress_pct=progress_pct,
            next_level_xp=next_xp_threshold,
            needed_steps=needed_steps
        ))

    # Sort by XP (highest first) or by progress
    items.sort(key=lambda x: x.current_xp, reverse=True)
    
    return schemas.SkillGapResponse(
        target_karir=current_user.target_karir or "Karir Impian",
        skills=items
    )


# --- CURRICULUM SYSTEM API ---

@router.get("/campuses", response_model=List[schemas.Campus])
def get_campuses(db: Session = Depends(get_db)):
    return crud.get_campuses(db)

@router.get("/campuses/{campus_id}/departments", response_model=List[schemas.Department])
def get_departments_by_campus(campus_id: int, db: Session = Depends(get_db)):
    return crud.get_departments_by_campus(db, campus_id)

@router.get("/departments/{department_id}/curricula", response_model=List[schemas.Curriculum])
def get_curricula_by_department(department_id: int, db: Session = Depends(get_db)):
    return crud.get_curricula_by_department(db, department_id)

@router.get("/curricula/{curriculum_id}/courses", response_model=List[schemas.Course])
def get_courses_by_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    return crud.get_courses_by_curriculum(db, curriculum_id)

@router.post("/import-kurikulum")
def import_kurikulum_batch(
    data: List[dict], 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Batch import curriculum data from CSV/Json"""
    # Logic for batch import (used by import script or admin UI)
    results = []
    for item in data:
        # 1. Campus
        campus = crud.get_campus_by_name(db, item["universitas"])
        if not campus:
            campus = crud.create_campus(db, schemas.CampusCreate(name=item["universitas"]))
        
        # 2. Department
        dept = crud.get_department_by_name_and_campus(db, item["jurusan"], campus.id)
        if not dept:
            dept = crud.create_department(db, schemas.DepartmentCreate(campus_id=campus.id, name=item["jurusan"]))
        
        # 3. Curriculum
        curr_semester = item.get("semester_type") or item.get("semester") # Handle both possible keys
        curr = crud.get_curriculum_by_dept_and_semester(db, dept.id, curr_semester)
        if not curr:
            curr = crud.create_curriculum(db, schemas.CurriculumCreate(department_id=dept.id, semester=curr_semester))
        
        # 4. Course
        course = crud.create_course(db, schemas.CourseCreate(
            curriculum_id=curr.id,
            code=item["kode_mk"],
            name=item["nama_mk"],
            sks=int(item["sks"]),
            semester_target=int(item["semester"]),
            is_elective=(item.get("kategori", "").lower() == "pilihan")
        ))
        results.append(course.id)
    
    return {"message": f"Successfully imported {len(results)} courses", "ids": results}

@router.post("/connect-curriculum")
def connect_curriculum(
    curriculum_id: int,
    id_semester: int,
    target_semester_level: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Automatically populate schedule from curriculum courses"""
    # Verify semester belongs to user
    semester = crud.get_semester(db, id_semester)
    if not semester or semester.id_user != current_user.id_user:
        raise HTTPException(status_code=404, detail="Semester not found or not authorized")
        
    results = crud.connect_curriculum_to_user(
        db, 
        current_user.id_user, 
        curriculum_id, 
        id_semester, 
        target_semester_level
    )
    
    return {"message": f"Connected {len(results)} courses to your schedule", "count": len(results)}


# ===================================================
# ADAPTIVE ROADMAP — Preview + Apply
# ===================================================

@router.post("/roadmap/{roadmap_id}/adapt/preview", response_model=schemas.AdaptRoadmapPreview)
async def adapt_roadmap_preview(
    roadmap_id: int,
    request: schemas.AdaptRoadmapRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    roadmap = db.query(models.Roadmap).filter_by(id=roadmap_id, id_user=current_user.id_user).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    steps = db.query(models.RoadmapStep).filter_by(id_roadmap=roadmap_id).order_by(
        models.RoadmapStep.step_order
    ).all()

    preview = await rag.adapt_roadmap_preview(roadmap, steps, current_user, request.user_message)
    return preview


@router.post("/roadmap/{roadmap_id}/adapt/apply")
async def adapt_roadmap_apply(
    roadmap_id: int,
    changes: list[schemas.AdaptedStep] = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    roadmap = db.query(models.Roadmap).filter_by(id=roadmap_id, id_user=current_user.id_user).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    for change in changes:
        if change.action == "remove" and change.id:
            step = db.query(models.RoadmapStep).filter_by(id=change.id).first()
            if step:
                db.delete(step)
        elif change.action == "edit" and change.id:
            step = db.query(models.RoadmapStep).filter_by(id=change.id).first()
            if step:
                for f in ["title", "description", "skill_tags", "xp_reward", "phase", "step_order"]:
                    v = getattr(change, f, None)
                    if v is not None:
                        setattr(step, f, v)
        elif change.action == "add":
            new_step = models.RoadmapStep(
                id_roadmap=roadmap_id,
                phase=change.phase or "Tambahan",
                step_order=change.step_order or 999,
                title=change.title or "Step Baru",
                description=change.description,
                skill_tags=change.skill_tags,
                xp_reward=change.xp_reward or 10
            )
            db.add(new_step)
            db.flush()
            db.add(models.CareerProgress(id_user=current_user.id_user, id_roadmap_step=new_step.id))

    db.commit()
    return {"message": f"Applied {len(changes)} changes to roadmap"}

