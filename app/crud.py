from sqlalchemy.orm import Session
from . import models, schemas
from pgvector.sqlalchemy import Vector
from typing import List, Optional
import json

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id_user == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        nama=user.nama,
        email=user.email,
        telepon=user.telepon,
        bio=user.bio,
        lokasi=user.lokasi,
        umur=user.umur,
        minat=user.minat,
        keterampilan=user.keterampilan,
        kepribadian=user.kepribadian,
        target_karir=user.target_karir,
        gaya_belajar=user.gaya_belajar,
        waktu_luang=user.waktu_luang
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id_user == user_id).first()
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            # ORM-style update (correct)
            for key, value in update_data.items():
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id_user == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_rags_embeddings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RAGSEmbedding).offset(skip).limit(limit).all()

def create_rags_embedding(db: Session, embedding: schemas.RAGSEmbeddingCreate, vector_embedding: List[float]):
    db_embedding = models.RAGSEmbedding(
        id_user=embedding.id_user,
        source_type=embedding.source_type,
        source_id=embedding.source_id,
        text_original=embedding.text_original,
        embedding=vector_embedding
    )
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding

def delete_rags_embedding(db: Session, embedding_id: int):
    db_embedding = db.query(models.RAGSEmbedding).filter(models.RAGSEmbedding.id_embedding == embedding_id).first()
    if db_embedding:
        db.delete(db_embedding)
        db.commit()
    return db_embedding

def delete_rags_embeddings_by_user_id(db: Session, user_id: int):
    db.query(models.RAGSEmbedding).filter(models.RAGSEmbedding.id_user == user_id).delete()
    db.commit()

def delete_rags_embedding_by_source_type_and_id(db: Session, source_type: str, source_id: str):
    db.query(models.RAGSEmbedding).filter(
        models.RAGSEmbedding.source_type == source_type,
        models.RAGSEmbedding.source_id == source_id
    ).delete()
    db.commit()

def create_ai_chat_history(db: Session, chat_entry: schemas.AIChatHistoryCreate):
    db_chat_entry = models.AIChatHistory(
        id_user=chat_entry.id_user,
        role=chat_entry.role,
        message=chat_entry.message
    )
    db.add(db_chat_entry)
    db.commit()
    db.refresh(db_chat_entry)
    return db_chat_entry

# --- TODO CRUD ---
def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    db_todo = models.Todo(
        id_user=todo.id_user,
        nama=todo.nama,
        tipe=todo.tipe,
        tenggat=todo.tenggat,
        deskripsi=todo.deskripsi,
        id_roadmap_step=getattr(todo, 'id_roadmap_step', None)
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo_update: schemas.TodoUpdate) -> Optional[models.Todo]:
    db_todo = db.query(models.Todo).filter(models.Todo.id_todo == todo_id).first()
    if db_todo:
        update_data = todo_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data: # Only execute update if there's data to update
            for key, value in update_data.items():
                setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo) # Refresh the in-memory object to reflect changes from the direct update
    return db_todo

def get_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    return db.query(models.Todo).filter(models.Todo.id_todo == todo_id).first()

def get_all_todos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Todo]:
    return db.query(models.Todo).offset(skip).limit(limit).all()

def get_todos_by_user(db: Session, id_user: int, skip: int = 0, limit: int = 100) -> List[models.Todo]:
    return db.query(models.Todo).filter(models.Todo.id_user == id_user).offset(skip).limit(limit).all()

def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id_todo == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo

# --- SEMESTER CRUD ---
def check_semester_overlap(db: Session, user_id: int, start_date, end_date, exclude_semester_id: int = None) -> bool:
    query = db.query(models.Semester).filter(
        models.Semester.id_user == user_id,
        models.Semester.tanggal_mulai <= end_date,
        models.Semester.tanggal_selesai >= start_date
    )
    if exclude_semester_id:
        query = query.filter(models.Semester.id_semester != exclude_semester_id)
    return query.first() is not None

def create_semester(db: Session, semester: schemas.SemesterCreate) -> models.Semester:
    db_semester = models.Semester(
        id_user=semester.id_user,
        tipe=semester.tipe,
        tahun_ajaran=semester.tahun_ajaran,
        tanggal_mulai=semester.tanggal_mulai,
        tanggal_selesai=semester.tanggal_selesai
    )
    db.add(db_semester)
    db.commit()
    db.refresh(db_semester)
    return db_semester

def get_semesters_by_user(db: Session, id_user: int, skip: int = 0, limit: int = 100) -> List[models.Semester]:
    return db.query(models.Semester).filter(models.Semester.id_user == id_user).offset(skip).limit(limit).all()

def get_semester(db: Session, semester_id: int) -> Optional[models.Semester]:
    return db.query(models.Semester).filter(models.Semester.id_semester == semester_id).first()

def delete_semester(db: Session, semester_id: int):
    db_semester = db.query(models.Semester).filter(models.Semester.id_semester == semester_id).first()
    if db_semester:
        db.delete(db_semester)
        db.commit()
    return db_semester

def update_semester(db: Session, semester_id: int, semester_update: schemas.SemesterUpdate) -> Optional[models.Semester]:
    db_semester = db.query(models.Semester).filter(models.Semester.id_semester == semester_id).first()
    if db_semester:
        update_data = semester_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            for key, value in update_data.items():
                setattr(db_semester, key, value)
        db.commit()
        db.refresh(db_semester)
    return db_semester


# --- JADWAL MATKUL CRUD ---
def create_jadwal_matkul(db: Session, jadwal: schemas.JadwalMatkulCreate) -> models.JadwalMatkul:
    db_jadwal = models.JadwalMatkul(
        id_user=jadwal.id_user,
        id_semester=jadwal.id_semester,
        hari=models.HariEnum(jadwal.hari), # Ensure Enum conversion
        nama=jadwal.nama,
        jam_mulai=jadwal.jam_mulai,
        jam_selesai=jadwal.jam_selesai,
        sks=jadwal.sks
    )
    db.add(db_jadwal)
    db.commit()
    db.refresh(db_jadwal)
    return db_jadwal

def update_jadwal_matkul(db: Session, jadwal_id: int, jadwal_update: schemas.JadwalMatkulUpdate) -> Optional[models.JadwalMatkul]:
    db_jadwal = db.query(models.JadwalMatkul).filter(models.JadwalMatkul.id_jadwal == jadwal_id).first()
    if db_jadwal:
        update_data = jadwal_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data: # Only execute update if there's data to update
            for key, value in update_data.items():
                setattr(db_jadwal, key, value)
        db.commit()
        db.refresh(db_jadwal) # Refresh the in-memory object to reflect changes from the direct update
    return db_jadwal

def get_jadwal_matkul(db: Session, jadwal_id: int) -> Optional[models.JadwalMatkul]:
    return db.query(models.JadwalMatkul).filter(models.JadwalMatkul.id_jadwal == jadwal_id).first()

def get_all_jadwal_matkul(db: Session, skip: int = 0, limit: int = 100) -> List[models.JadwalMatkul]:
    return db.query(models.JadwalMatkul).offset(skip).limit(limit).all()

def get_jadwal_matkul_by_user(db: Session, id_user: int, skip: int = 0, limit: int = 100) -> List[models.JadwalMatkul]:
    # Eager load semester details for display if needed
    return db.query(models.JadwalMatkul).filter(models.JadwalMatkul.id_user == id_user).offset(skip).limit(limit).all()

def delete_jadwal_matkul(db: Session, jadwal_id: int):
    db_jadwal = db.query(models.JadwalMatkul).filter(models.JadwalMatkul.id_jadwal == jadwal_id).first()
    if db_jadwal:
        db.delete(db_jadwal)
        db.commit()
    return db_jadwal

def get_jadwal_matkul_by_semester(db: Session, id_semester: int, skip: int = 0, limit: int = 100) -> List[models.JadwalMatkul]:
    return db.query(models.JadwalMatkul).filter(models.JadwalMatkul.id_semester == id_semester).offset(skip).limit(limit).all()

# --- UKM CRUD ---
def create_ukm(db: Session, ukm: schemas.UKMCreate) -> models.UKM:
    db_ukm = models.UKM(
        id_user=ukm.id_user,
        nama=ukm.nama,
        jabatan=ukm.jabatan,
        deskripsi=ukm.deskripsi
    )
    db.add(db_ukm)
    db.commit()
    db.refresh(db_ukm)
    return db_ukm

def update_ukm(db: Session, ukm_id: int, ukm_update: schemas.UKMUpdate) -> Optional[models.UKM]:
    db_ukm = db.query(models.UKM).filter(models.UKM.id_ukm == ukm_id).first()
    if db_ukm:
        update_data = ukm_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data: # Only execute update if there's data to update
            for key, value in update_data.items():
                setattr(db_ukm, key, value)
        db.commit()
        db.refresh(db_ukm) # Refresh the in-memory object to reflect changes from the direct update
    return db_ukm

def get_ukm(db: Session, ukm_id: int) -> Optional[models.UKM]:
    return db.query(models.UKM).filter(models.UKM.id_ukm == ukm_id).first()

def get_all_ukm(db: Session, skip: int = 0, limit: int = 100) -> List[models.UKM]:
    return db.query(models.UKM).offset(skip).limit(limit).all()

def get_ukm_by_user(db: Session, id_user: int, skip: int = 0, limit: int = 100) -> List[models.UKM]:
    return db.query(models.UKM).filter(models.UKM.id_user == id_user).offset(skip).limit(limit).all()

def delete_ukm(db: Session, ukm_id: int):
    db_ukm = db.query(models.UKM).filter(models.UKM.id_ukm == ukm_id).first()
    if db_ukm:
        db.delete(db_ukm)
        db.commit()
    return db_ukm


# --- RUTINITAS CRUD ---
def create_rutinitas(db: Session, rutinitas: schemas.RutinitasCreate) -> models.Rutinitas:
    db_rutinitas = models.Rutinitas(
        id_user=rutinitas.id_user,
        nama=rutinitas.nama,
        hari=rutinitas.hari,
        jam_mulai=rutinitas.jam_mulai,
        jam_selesai=rutinitas.jam_selesai,
        deskripsi=rutinitas.deskripsi
    )
    db.add(db_rutinitas)
    db.commit()
    db.refresh(db_rutinitas)
    return db_rutinitas

def update_rutinitas(db: Session, rutinitas_id: int, rutinitas_update: schemas.RutinitasUpdate) -> Optional[models.Rutinitas]:
    db_rutinitas = db.query(models.Rutinitas).filter(models.Rutinitas.id_rutinitas == rutinitas_id).first()
    if db_rutinitas:
        update_data = rutinitas_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            for key, value in update_data.items():
                setattr(db_rutinitas, key, value)
        db.commit()
        db.refresh(db_rutinitas)
    return db_rutinitas

def get_rutinitas(db: Session, rutinitas_id: int) -> Optional[models.Rutinitas]:
    return db.query(models.Rutinitas).filter(models.Rutinitas.id_rutinitas == rutinitas_id).first()

def get_rutinitas_by_user(db: Session, id_user: int, skip: int = 0, limit: int = 100) -> List[models.Rutinitas]:
    return db.query(models.Rutinitas).filter(models.Rutinitas.id_user == id_user).offset(skip).limit(limit).all()

def delete_rutinitas(db: Session, rutinitas_id: int):
    db_rutinitas = db.query(models.Rutinitas).filter(models.Rutinitas.id_rutinitas == rutinitas_id).first()
    if db_rutinitas:
        db.delete(db_rutinitas)
        db.commit()
    return db_rutinitas


def get_chat_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AIChatHistory).filter(models.AIChatHistory.id_user == user_id).offset(skip).limit(limit).all()

def get_all_rags_embeddings(db: Session):
    return db.query(models.RAGSEmbedding).all()

from .rag import embed_text_with_gemini # Import the embedding function

async def create_user_embedding(db: Session, db_user: models.User):
    # Combine relevant user data into a single text for embedding
    user_data_text = f"Nama: {db_user.nama}. Email: {db_user.email}. Telepon: {db_user.telepon or ''}. Bio: {db_user.bio or ''}. Lokasi: {db_user.lokasi or ''}."
    
    # Generate embedding
    user_embedding_vector = await embed_text_with_gemini(user_data_text)
    
    # Create RAGSEmbedding entry
    db_embedding = models.RAGSEmbedding(
        id_user=db_user.id_user,
        source_type="user",
        source_id=str(db_user.id_user), # Use user ID as source_id
        text_original=user_data_text,
        embedding=user_embedding_vector
    )
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding


# --- CAREER RESULT CRUD ---
def save_career_result(db: Session, user_id: int, data: dict):
    career = models.CareerResult(
        id_user=user_id,
        career_name=data["career"]["name"],
        reason=data["career"]["reason"],
        strengths=json.dumps(data["career"]["strengths"]),
        weaknesses=json.dumps(data["career"]["weaknesses"])
    )
    db.add(career)
    db.commit()
    db.refresh(career)

    return career.id

def create_career_result(db: Session, result: schemas.CareerResultCreate) -> models.CareerResult:
    db_result = models.CareerResult(
        id_user=result.id_user,
        career_name=result.career_name,
        reason=result.reason,
        strengths=result.strengths,
        weaknesses=result.weaknesses
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_career_results_by_user(db: Session, id_user: int) -> List[models.CareerResult]:
    return db.query(models.CareerResult).filter(models.CareerResult.id_user == id_user).all()

def delete_career_result(db: Session, result_id: int):
    db_result = db.query(models.CareerResult).filter(models.CareerResult.id == result_id).first()
    if db_result:
        db.delete(db_result)
        db.commit()
    return db_result


# --- ROADMAP CRUD ---
def create_roadmap(db: Session, roadmap: schemas.RoadmapCreate) -> models.Roadmap:
    db_roadmap = models.Roadmap(
        id_user=roadmap.id_user,
        id_career=roadmap.id_career,
        title=roadmap.title
    )
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    return db_roadmap

def get_roadmaps_by_user(db: Session, id_user: int) -> List[models.Roadmap]:
    return db.query(models.Roadmap).filter(models.Roadmap.id_user == id_user).all()

def delete_roadmap(db: Session, roadmap_id: int):
    db_roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if db_roadmap:
        db.delete(db_roadmap)
        db.commit()
    return db_roadmap


# --- ROADMAP STEP CRUD ---
def create_roadmap_step(db: Session, step: schemas.RoadmapStepCreate) -> models.RoadmapStep:
    db_step = models.RoadmapStep(
        id_roadmap=step.id_roadmap,
        phase=step.phase,
        step_order=step.step_order,
        title=step.title,
        description=step.description,
        skill_tags=getattr(step, 'skill_tags', None),
        xp_reward=getattr(step, 'xp_reward', 10)
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step

def get_roadmap_steps_by_roadmap(db: Session, id_roadmap: int) -> List[models.RoadmapStep]:
    return db.query(models.RoadmapStep).filter(models.RoadmapStep.id_roadmap == id_roadmap).order_by(models.RoadmapStep.step_order).all()

def delete_roadmap_step(db: Session, step_id: int):
    db_step = db.query(models.RoadmapStep).filter(models.RoadmapStep.id == step_id).first()
    if db_step:
        db.delete(db_step)
        db.commit()
    return db_step


# --- CAREER PROGRESS CRUD ---
def create_career_progress(db: Session, progress: schemas.CareerProgressCreate) -> models.CareerProgress:
    db_progress = models.CareerProgress(
        id_user=progress.id_user,
        id_roadmap_step=progress.id_roadmap_step,
        status=progress.status,
        completed_at=progress.completed_at
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def get_career_progress_by_user(db: Session, id_user: int) -> List[models.CareerProgress]:
    return db.query(models.CareerProgress).filter(models.CareerProgress.id_user == id_user).all()

def update_career_progress(db: Session, progress_id: int, progress_update: schemas.CareerProgressUpdate) -> Optional[models.CareerProgress]:
    db_progress = db.query(models.CareerProgress).filter(models.CareerProgress.id == progress_id).first()
    if db_progress:
        update_data = progress_update.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            for key, value in update_data.items():
                setattr(db_progress, key, value)
        db.commit()
        db.refresh(db_progress)
    return db_progress


