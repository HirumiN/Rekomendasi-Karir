from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, time, date
import logging
import traceback

from . import models, schemas, crud, db, rag, auth, api, rag_service
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    db.Base.metadata.create_all(bind=db.engine)
    db.create_hnsw_index()
    yield

app = FastAPI(lifespan=lifespan)

# Load allowed CORS origins dynamically
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=auth.SECRET_KEY)

app.include_router(api.router)

@app.exception_handler(HTTPException)
async def cors_aware_http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler that adds CORS headers to error responses.
    This fixes the browser showing 'CORS error' when the real issue is 401/403.
    """
    origin = request.headers.get("origin", "")
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.exception_handler(Exception)
async def cors_aware_generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler: covers ResponseValidationError (500) and any unhandled exceptions.
    Ensures CORS headers are always present so the real error is visible in frontend.
    """
    import traceback
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    origin = request.headers.get("origin", "")
    response = JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

from .db import get_db

# Simple root for HTML (legacy, kept for compatibility)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return HTMLResponse("<h1>Campus AI Backend Running</h1>")

# --- AUTH ROUTES (Email/Password) ---

@app.post("/auth/register")
async def register(body: schemas.UserRegister, request: Request, db_session: Session = Depends(get_db)):
    # Check duplicate email
    if crud.get_user_by_email(db_session, body.email):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")

    new_user = models.User(
        nama=body.nama,
        email=body.email,
        password_hash=auth.hash_password(body.password),
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    try:
        await crud.create_user_embedding(db_session, new_user)
    except Exception as e:
        logger.warning(f"Embedding creation failed on register: {e}")

    request.session['user_id'] = new_user.id_user
    return {"message": "Akun berhasil dibuat.", "user_id": new_user.id_user}

@app.post("/auth/login")
async def login_email(body: schemas.UserLogin, request: Request, db_session: Session = Depends(get_db)):
    db_user = None
    if "@" in body.identifier:
        db_user = crud.get_user_by_email(db_session, body.identifier)
    else:
        db_user = crud.get_user_by_nama(db_session, body.identifier)
        
    if not db_user or not db_user.password_hash:
        raise HTTPException(status_code=401, detail="Username/Email atau password salah.")
    if not auth.verify_password(body.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Username/Email atau password salah.")
    request.session['user_id'] = db_user.id_user
    return {"message": "Login berhasil.", "user_id": db_user.id_user}

@app.post("/auth/logout")
async def logout(request: Request):
    request.session.pop('user_id', None)
    return {"message": "Logout berhasil."}

# Legacy GET logout redirect (for safety)
@app.get("/logout")
async def logout_get(request: Request):
    request.session.pop('user_id', None)
    return JSONResponse({"message": "Logout berhasil."})






@app.post("/onboarding", response_class=RedirectResponse)
async def onboarding_submit(
    request: Request,
    telepon: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    lokasi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    user = await auth.get_current_user(request, db_session)
    if not user:
        return RedirectResponse(url="/")
    
    user_update = schemas.UserUpdate(
        telepon=telepon,
        bio=bio,
        lokasi=lokasi
    )
    crud.update_user(db_session, user.id_user, user_update)
    
    # Regnerate embedding using service
    await rag_service.update_user_embedding(db_session, user)
    
    return RedirectResponse(url="/", status_code=303)



# POST /add-user
@app.post("/add-user", response_class=RedirectResponse)
async def add_user(
    nama: str = Form(...),
    email: str = Form(...),
    telepon: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    lokasi: Optional[str] = Form(None),
    umur: Optional[int] = Form(None),
    minat: Optional[str] = Form(None),
    keterampilan: Optional[str] = Form(None),
    kepribadian: Optional[str] = Form(None),
    target_karir: Optional[str] = Form(None),
    gaya_belajar: Optional[str] = Form(None),
    waktu_luang: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        user_create = schemas.UserCreate(
            nama=nama,
            email=email,
            telepon=telepon,
            bio=bio,
            lokasi=lokasi,
            umur=umur,
            minat=minat,
            keterampilan=keterampilan,
            kepribadian=kepribadian,
            target_karir=target_karir,
            gaya_belajar=gaya_belajar,
            waktu_luang=waktu_luang
        )
        db_user = crud.create_user(db_session, user_create)
        await rag_service.update_user_embedding(db_session, db_user) # Create embedding for the new user using service
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Background task to auto-generate and save career analysis and roadmap upon onboarding completion
async def generate_and_save_career_roadmap_task(user_id: int):
    from app.db import SessionLocal
    from app import crud, models, rag, schemas, rag_service
    import json
    from datetime import datetime
    import logging

    db = SessionLocal()
    try:
        logging.info(f"Background task starting: generating career analysis and roadmap for user {user_id}")
        
        # 1. Generate career analysis
        data = await rag.generate_career_analysis(db, user_id)
        
        # 2. Delete old roadmap data (same logic as save_career_analysis_api)
        db.query(models.Roadmap).filter_by(id_user=user_id).delete()
        db.query(models.CareerResult).filter_by(id_user=user_id).delete()
        db.query(models.Todo).filter(
            models.Todo.id_user == user_id, 
            models.Todo.deskripsi == "Dari Analisis Karir AI."
        ).delete()
        db.query(models.UserSkillXP).filter_by(id_user=user_id).delete()
        
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
            primary_career_id = crud.save_career_result(db, user_id, data)
            career_name = data.get("career", {}).get("name", "Career Analysis")
        else:
            logging.error("Invalid generation data format inside background task")
            return

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
                    skill_tags_raw = step.get("skill_tags")
                    if isinstance(skill_tags_raw, list):
                        skill_tags_raw = json.dumps(skill_tags_raw)
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

        # Insert Tasks as Todos
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

        # Perform all embeddings in parallel
        if todo_embedding_tasks:
            import asyncio
            await asyncio.gather(*todo_embedding_tasks)

        db.commit()
        logging.info(f"Background task finished successfully: career analysis and roadmap saved for user {user_id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error in background career generation task: {e}")
    finally:
        db.close()


# POST /update-user/{user_id}
@app.post("/update-user/{user_id}", response_class=RedirectResponse)
async def update_user_route(
    user_id: int,
    background_tasks: BackgroundTasks,
    nama: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    telepon: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    lokasi: Optional[str] = Form(None),
    umur: Optional[int] = Form(None),
    minat: Optional[str] = Form(None),
    keterampilan: Optional[str] = Form(None),
    kepribadian: Optional[str] = Form(None),
    target_karir: Optional[str] = Form(None),
    gaya_belajar: Optional[str] = Form(None),
    waktu_luang: Optional[str] = Form(None),
    universitas: Optional[str] = Form(None),
    jurusan: Optional[str] = Form(None),
    semester_sekarang: Optional[str] = Form(None),
    calendar_name: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        # Check if name changed for sync trigger
        user_update_data = schemas.UserUpdate(
            nama=nama,
            email=email,
            telepon=telepon,
            bio=bio,
            lokasi=lokasi,
            umur=umur,
            minat=minat,
            keterampilan=keterampilan,
            kepribadian=kepribadian,
            target_karir=target_karir,
            gaya_belajar=gaya_belajar,
            waktu_luang=waktu_luang,
            universitas=universitas,
            jurusan=jurusan,
            semester_sekarang=semester_sekarang,
            calendar_name=calendar_name
        )
        
        # We need to know if academic fields changed to trigger auto-connect
        current_db_user = crud.get_user(db_session, user_id)
        academic_was_empty = not current_db_user.universitas or not current_db_user.jurusan
        academic_changed = (
            (universitas and universitas != current_db_user.universitas) or
            (jurusan and jurusan != current_db_user.jurusan) or
            (semester_sekarang and semester_sekarang != current_db_user.semester_sekarang)
        )
        
        db_user = crud.update_user(db_session, user_id, user_update_data)
        
        # Trigger full resync if calendar name changed
        # if db_user and db_user.calendar_name != old_cal_name:
        #      # This will rename all semester calendars
        #      calendar_service.resync_all_user_calendars(db_session, db_user)

        if db_user:
            # Re-generate and update user embedding if user data was changed
            await rag_service.update_user_embedding(db_session, db_user)
            
            # Trigger auto-connect curriculum if campus/department changed, OR if no schedules exist yet
            existing_schedules = crud.get_jadwal_matkul_by_user(db_session, user_id)
            campus_or_dept_changed = (
                (universitas and universitas != current_db_user.universitas) or
                (jurusan and jurusan != current_db_user.jurusan)
            )
            needs_curriculum_connect = (campus_or_dept_changed or not existing_schedules)

            if needs_curriculum_connect and db_user.universitas and db_user.jurusan and db_user.semester_sekarang:
                # Find matching curriculum
                campus = db_session.query(models.Campus).filter(models.Campus.name == db_user.universitas).first()
                if campus:
                    dept = db_session.query(models.Department).filter(
                        models.Department.campus_id == campus.id,
                        models.Department.name == db_user.jurusan
                    ).first()
                    if dept:
                        curricula = db_session.query(models.Curriculum).filter(models.Curriculum.department_id == dept.id).all()
                        if curricula:
                            # 1. Clear existing schedule first to prevent duplicates / mixed curricula
                            crud.delete_all_user_jadwal(db_session, user_id)
                            
                            # 2. Auto connect for ALL semesters (1-8) walking through all curriculum types (Ganjil/Genap)
                            new_schedules = []
                            for curr_obj in curricula:
                                for s_l in range(1, 9):
                                    created = crud.connect_curriculum_to_user(db_session, user_id, curr_obj.id, None, s_l)
                                    new_schedules.extend(created)
                            
                            # 3. Generate embeddings in parallel for all newly connected schedules to allow immediate AI retrieval
                            if new_schedules:
                                import asyncio
                                embedding_tasks = [
                                    rag_service.update_jadwal_embedding(db_session, s, commit=False)
                                    for s in new_schedules
                                ]
                                await asyncio.gather(*embedding_tasks)
                                db_session.commit()

        # Check if onboarding just completed (user filled all major profile fields during this step)
        is_onboarding_submission = (
            umur is not None and
            universitas is not None and
            jurusan is not None and
            target_karir is not None
        )
        if is_onboarding_submission:
            background_tasks.add_task(generate_and_save_career_roadmap_task, user_id)

        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# POST /delete-user/{user_id}

@app.post("/delete-user/{user_id}", response_class=RedirectResponse)

async def delete_user_route(user_id: int, db_session: Session = Depends(get_db)):

    crud.delete_user(db_session, user_id)

    crud.delete_rags_embeddings_by_user_id(db_session, user_id) # Delete all related embeddings

    return RedirectResponse(url="/", status_code=303)



# --- JSON List Endpoints for Frontend ---



# GET /users

@app.get("/users", response_model=List[schemas.User])

async def get_users_json(db_session: Session = Depends(get_db)):

    users = crud.get_users(db_session)

    return users



# GET /todos

@app.get("/todos", response_model=List[schemas.Todo])

async def get_todos_json(

    id_user: Optional[int] = None,

    db_session: Session = Depends(get_db)

):

    if id_user:

        todos = crud.get_todos_by_user(db_session, id_user)

    else:

        todos = crud.get_all_todos(db_session)

    return todos



# GET /jadwal

@app.get("/jadwal", response_model=List[schemas.JadwalMatkul])

async def get_jadwal_json(

    id_user: Optional[int] = None,

    db_session: Session = Depends(get_db)

):

    if id_user:

        jadwal = crud.get_jadwal_matkul_by_user(db_session, id_user)

    else:

        jadwal = crud.get_all_jadwal_matkul(db_session)

    return jadwal



# GET /ukm

@app.get("/ukm", response_model=List[schemas.UKM])

async def get_ukm_json(

    id_user: Optional[int] = None,

    db_session: Session = Depends(get_db)

):

    if id_user:

        ukm = crud.get_ukm_by_user(db_session, id_user)

    else:

        ukm = crud.get_all_ukm(db_session)

    return ukm

# GET /chat-history/{user_id}
@app.get("/chat-history/{user_id}", response_model=List[schemas.AIChatHistory])
async def get_user_chat_history(user_id: int, db_session: Session = Depends(get_db)):
    chat_history = crud.get_chat_history(db_session, user_id)
    return chat_history





# --- TODO Endpoints ---
@app.post("/add-todo", response_class=RedirectResponse)
async def add_todo(
    request: Request,
    id_user: int = Form(...),
    nama: str = Form(...),
    tipe: str = Form(...),
    tenggat: Optional[str] = Form(None), # Receive as string, parse later
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        tenggat_dt = datetime.fromisoformat(tenggat) if tenggat else None
        todo_create = schemas.TodoCreate(
            id_user=id_user,
            nama=nama,
            tipe=tipe,
            tenggat=tenggat_dt,
            deskripsi=deskripsi
        )
        db_todo = crud.create_todo(db_session, todo_create)
        
        # Calendar Sync (Phase 2)
        # db_user = crud.get_user(db_session, id_user)
        # if db_user and db_user.access_token and tenggat_dt:
        #      # Use the new service that handles dedicated calendar
        #      event_id = calendar_service.create_todo_event(db_session, db_user, db_todo)
        #      if event_id:
        #          db_todo.google_event_id = event_id
        #          db_session.commit()
        
        await rag_service.update_todo_embedding(db_session, db_todo)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-todo/{todo_id}", response_class=RedirectResponse)
async def delete_todo_route(todo_id: int, db_session: Session = Depends(get_db)):
    # Check for calendar event to delete
    db_todo = crud.get_todo(db_session, todo_id)
    if db_todo and db_todo.google_event_id:
         db_user = crud.get_user(db_session, db_todo.id_user)
         if db_user:
             pass

    crud.delete_todo(db_session, todo_id)
    crud.delete_rags_embedding_by_source_type_and_id(db_session, "todo", str(todo_id))
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-todo/{todo_id}", response_class=RedirectResponse)
async def update_todo_route(
    todo_id: int,
    id_user: Optional[int] = Form(None),
    nama: Optional[str] = Form(None),
    tipe: Optional[str] = Form(None),
    tenggat: Optional[str] = Form(None), # Receive as string, parse later
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        tenggat_dt = datetime.fromisoformat(tenggat) if tenggat else None
        todo_update_data = schemas.TodoUpdate(
            id_user=id_user,
            nama=nama,
            tipe=tipe,
            tenggat=tenggat_dt,
            deskripsi=deskripsi
        )
        db_todo = crud.update_todo(db_session, todo_id, todo_update_data)

        if db_todo:
            # Re-generate and update embedding using service
            await rag_service.update_todo_embedding(db_session, db_todo)

        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# --- JADWAL MATKUL Endpoints ---
@app.post("/add-jadwal", response_class=RedirectResponse)
async def add_jadwal(
    id_user: int = Form(...),
    id_semester: Optional[int] = Form(None),
    hari: str = Form(...),
    nama: str = Form(...),
    jam_mulai: str = Form(...), # Receive as string, parse later
    jam_selesai: str = Form(...), # Receive as string, parse later
    sks: int = Form(...),
    db_session: Session = Depends(get_db)
):
    try:
        jam_mulai_time = time.fromisoformat(jam_mulai)
        jam_selesai_time = time.fromisoformat(jam_selesai)
        
        jadwal_create = schemas.JadwalMatkulCreate(
            id_user=id_user,
            id_semester=id_semester,
            hari=hari,
            nama=nama,
            jam_mulai=jam_mulai_time,
            jam_selesai=jam_selesai_time,
            sks=sks
        )
        db_jadwal = crud.create_jadwal_matkul(db_session, jadwal_create)
        
        # Calendar Sync (Phase 2: Recurring)
        # if id_semester:
        #      db_semester = crud.get_semester(db_session, id_semester)
        #      db_user = crud.get_user(db_session, id_user)
        #      if db_semester and db_user and db_user.access_token:
        #          event_id = calendar_service.create_recurring_class_event(db_session, db_user, db_semester, db_jadwal)
        #          if event_id:
        #              db_jadwal.google_event_id = event_id
        #              db_session.commit()
        
        await rag_service.update_jadwal_embedding(db_session, db_jadwal)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-jadwal/{jadwal_id}", response_class=RedirectResponse)
async def delete_jadwal_route(jadwal_id: int, db_session: Session = Depends(get_db)):
    db_jadwal = crud.get_jadwal_matkul(db_session, jadwal_id)
    if db_jadwal and db_jadwal.google_event_id and db_jadwal.id_semester:
        # Need semester to know calendar ID
        db_semester = crud.get_semester(db_session, db_jadwal.id_semester)
        db_user = crud.get_user(db_session, db_jadwal.id_user)
        # if db_semester and db_semester.google_calendar_id and db_user:
        #     calendar_service.delete_event(db_session, db_user, db_jadwal.google_event_id, calendar_id=db_semester.google_calendar_id)

    crud.delete_jadwal_matkul(db_session, jadwal_id)
    crud.delete_rags_embedding_by_source_type_and_id(db_session, "jadwal", str(jadwal_id))
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-jadwal/{jadwal_id}", response_class=RedirectResponse)
async def update_jadwal_route(
    jadwal_id: int,
    id_user: Optional[int] = Form(None),
    id_semester: Optional[int] = Form(None),
    hari: Optional[str] = Form(None),
    nama: Optional[str] = Form(None),
    jam_mulai: Optional[str] = Form(None), # Receive as string, parse later
    jam_selesai: Optional[str] = Form(None), # Receive as string, parse later
    sks: Optional[int] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        jam_mulai_time = time.fromisoformat(jam_mulai) if jam_mulai else None
        jam_selesai_time = time.fromisoformat(jam_selesai) if jam_selesai else None
        jadwal_update_data = schemas.JadwalMatkulUpdate(
            id_user=id_user,
            id_semester=id_semester,
            hari=hari,
            nama=nama,
            jam_mulai=jam_mulai_time,
            jam_selesai=jam_selesai_time,
            sks=sks
        )
        db_jadwal = crud.update_jadwal_matkul(db_session, jadwal_id, jadwal_update_data)

        if db_jadwal:
            # Re-generate and update embedding using service
            await rag_service.update_jadwal_embedding(db_session, db_jadwal)
            
            # Calendar Sync Update (Phase 2.5)
            # if db_jadwal.id_semester and db_jadwal.google_event_id:
            #      db_semester = crud.get_semester(db_session, db_jadwal.id_semester)
            #      db_user = crud.get_user(db_session, db_jadwal.id_user)
            # if db_semester and db_user:
            #     calendar_service.update_recurring_event(db_session, db_user, db_semester, db_jadwal)
            pass

        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-ukm", response_class=RedirectResponse)
async def add_ukm(
    id_user: int = Form(...),
    nama: str = Form(...),
    jabatan: str = Form(...),
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        ukm_create = schemas.UKMCreate(
            id_user=id_user,
            nama=nama,
            jabatan=jabatan,
            deskripsi=deskripsi
        )
        db_ukm = crud.create_ukm(db_session, ukm_create)
        
        await rag_service.update_ukm_embedding(db_session, db_ukm)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-ukm/{ukm_id}", response_class=RedirectResponse)
async def delete_ukm_route(ukm_id: int, db_session: Session = Depends(get_db)):
    crud.delete_ukm(db_session, ukm_id)
    crud.delete_rags_embedding_by_source_type_and_id(db_session, "ukm", str(ukm_id))
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-ukm/{ukm_id}", response_class=RedirectResponse)
async def update_ukm_route(
    ukm_id: int,
    id_user: Optional[int] = Form(None),
    nama: Optional[str] = Form(None),
    jabatan: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        ukm_update_data = schemas.UKMUpdate(
            id_user=id_user,
            nama=nama,
            jabatan=jabatan,
            deskripsi=deskripsi
        )
        db_ukm = crud.update_ukm(db_session, ukm_id, ukm_update_data)

        if db_ukm:
            # Re-generate and update embedding using service
            await rag_service.update_ukm_embedding(db_session, db_ukm)

        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



# --- RUTINITAS Endpoints ---
@app.get("/rutinitas", response_model=List[schemas.Rutinitas])
async def get_rutinitas_json(
    id_user: Optional[int] = None,
    db_session: Session = Depends(get_db)
):
    if id_user:
        rutinitas = crud.get_rutinitas_by_user(db_session, id_user)
    else:
        rutinitas = []
    return rutinitas

@app.post("/add-rutinitas", response_class=RedirectResponse)
async def add_rutinitas(
    id_user: int = Form(...),
    nama: str = Form(...),
    hari: str = Form(...),
    jam_mulai: Optional[str] = Form(None),
    jam_selesai: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        jam_mulai_time = time.fromisoformat(jam_mulai) if jam_mulai else None
        jam_selesai_time = time.fromisoformat(jam_selesai) if jam_selesai else None
        rut_create = schemas.RutinitasCreate(
            id_user=id_user,
            nama=nama,
            hari=hari,
            jam_mulai=jam_mulai_time,
            jam_selesai=jam_selesai_time,
            deskripsi=deskripsi
        )
        db_rut = crud.create_rutinitas(db_session, rut_create)
        
        await rag_service.update_rutinitas_embedding(db_session, db_rut)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-rutinitas/{rutinitas_id}", response_class=RedirectResponse)
async def delete_rutinitas_route(rutinitas_id: int, db_session: Session = Depends(get_db)):
    crud.delete_rutinitas(db_session, rutinitas_id)
    crud.delete_rags_embedding_by_source_type_and_id(db_session, "rutinitas", str(rutinitas_id))
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-rutinitas/{rutinitas_id}", response_class=RedirectResponse)
async def update_rutinitas_route(
    rutinitas_id: int,
    id_user: Optional[int] = Form(None),
    nama: Optional[str] = Form(None),
    hari: Optional[str] = Form(None),
    jam_mulai: Optional[str] = Form(None),
    jam_selesai: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        jam_mulai_time = time.fromisoformat(jam_mulai) if jam_mulai else None
        jam_selesai_time = time.fromisoformat(jam_selesai) if jam_selesai else None
        rut_update_data = schemas.RutinitasUpdate(
            id_user=id_user,
            nama=nama,
            hari=hari,
            jam_mulai=jam_mulai_time,
            jam_selesai=jam_selesai_time,
            deskripsi=deskripsi
        )
        db_rut = crud.update_rutinitas(db_session, rutinitas_id, rut_update_data)

        if db_rut:
            await rag_service.update_rutinitas_embedding(db_session, db_rut)

        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# POST /rag/query (Section 8)
@app.post("/rag/query", response_model=schemas.RAGResponse)
async def rag_query(query: schemas.RAGQuery, db_session: Session = Depends(get_db)):
    try:
        # 1. Embed question
        query_embedding = await rag.embed_text_with_gemini(query.question)
        
        # 2. Find similar rows
        context_docs = rag.retrieve_similar_rags(db_session, query_embedding, query.top_k, query.id_user)
        
        # 3. Fetch user profile and class schedules for explicit omnipresent context
        user_record = None
        user_schedules = []
        if query.id_user:
            user_record = crud.get_user(db_session, query.id_user)
            user_schedules = db_session.query(models.JadwalMatkul).filter(
                models.JadwalMatkul.id_user == query.id_user
            ).all()

        # 4. Build augmented prompt with profile & schedule context
        augmented_prompt = rag.augment_prompt(
            query.question, 
            context_docs, 
            query.client_local_time, 
            user_record,
            user_schedules
        )
        
        # 5. Call Gemini generate
        answer = await rag.generate_answer_with_gemini(augmented_prompt)

        # 5. Save chat history (for user question)
        if query.id_user:
            crud.create_ai_chat_history(db_session, schemas.AIChatHistoryCreate(
                id_user=query.id_user, role="user", message=query.question
            ))
            crud.create_ai_chat_history(db_session, schemas.AIChatHistoryCreate(
                id_user=query.id_user, role="assistant", message=answer
            ))
        
        return schemas.RAGResponse(answer=answer, context_docs=context_docs)
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Optional: POST /calendar/create-event (Section 13)
@app.post("/calendar/sync", response_class=RedirectResponse)
async def manual_calendar_sync(request: Request, db_session: Session = Depends(get_db)):
    # user = await auth.get_current_user(request, db_session)
    # if user:
    #     calendar_service.sync_todos_to_calendar(db_session, user)
    return RedirectResponse(url="/", status_code=303)


# --- SEMESTER Endpoints (Phase 2) ---
@app.post("/add-semester", response_class=RedirectResponse)
async def add_semester(
    request: Request,
    tipe: str = Form(...),
    tahun_ajaran: str = Form(...),
    tanggal_mulai: str = Form(...),
    tanggal_selesai: str = Form(...),
    db_session: Session = Depends(get_db)
):
    user = await auth.get_current_user(request, db_session)
    if not user:
         return RedirectResponse(url="/")
         
    try:
        tanggal_mulai_date = date.fromisoformat(tanggal_mulai)
        tanggal_selesai_date = date.fromisoformat(tanggal_selesai)
        
        if crud.check_semester_overlap(db_session, user.id_user, tanggal_mulai_date, tanggal_selesai_date):
            raise HTTPException(status_code=400, detail="Periode semester tumpang tindih dengan semester yang sudah ada.")

        semester_create = schemas.SemesterCreate(
            id_user=user.id_user,
            tipe=tipe,
            tahun_ajaran=tahun_ajaran,
            tanggal_mulai=tanggal_mulai_date,
            tanggal_selesai=tanggal_selesai_date
        )
        new_sem = crud.create_semester(db_session, semester_create)
        
        # Auto-create calendar immediately
        # calendar_service.create_semester_calendar(db_session, user, new_sem)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating semester: {e}")
        logger.error(traceback.format_exc())
        
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete-semester/{semester_id}", response_class=RedirectResponse)
async def delete_semester(semester_id: int, request: Request, db_session: Session = Depends(get_db)):
    user = await auth.get_current_user(request, db_session)
    if not user:
         return RedirectResponse(url="/")
         
    db_semester = crud.get_semester(db_session, semester_id)
    if db_semester:
        # 1. Delete Google Calendar if exists
        # if db_semester.google_calendar_id:
        #     try:
        #         calendar_service.delete_calendar(user, db_semester.google_calendar_id)
        #     except Exception as e:
        #         logger.error(f"Failed to delete Google Calendar: {e}")
        
        # 2. Delete embeddings for all schedules in this semester
        for jadwal in db_semester.jadwal_matkul:
             crud.delete_rags_embedding_by_source_type_and_id(db_session, "jadwal", str(jadwal.id_jadwal))
             
        crud.delete_semester(db_session, semester_id)

    return RedirectResponse(url="/", status_code=303)


@app.post("/update-semester/{semester_id}", response_class=RedirectResponse)
async def update_semester(
    semester_id: int, 
    request: Request, 
    tipe: str = Form(...),
    tahun_ajaran: str = Form(...),
    db_session: Session = Depends(get_db)
):
    user = await auth.get_current_user(request, db_session)
    if not user:
         return RedirectResponse(url="/")
         
    db_semester = crud.get_semester(db_session, semester_id)
    if db_semester:
        db_semester.tipe = tipe
        db_semester.tahun_ajaran = tahun_ajaran
        db_session.commit()
        
        # Sync Calendar Name
        # if db_semester.google_calendar_id:
        #     new_summary = f"My Campus - {tipe} {tahun_ajaran}"
        #     calendar_service.update_calendar_metadata(user, db_semester.google_calendar_id, new_summary)
            
    return RedirectResponse(url="/", status_code=303)

