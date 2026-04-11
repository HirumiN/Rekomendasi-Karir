from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, time, date

# User Schemas
class UserBase(BaseModel):
    nama: str
    email: str
    username: Optional[str] = None
    telepon: Optional[str] = None
    bio: Optional[str] = None
    lokasi: Optional[str] = None
    umur: Optional[int] = None
    minat: Optional[str] = None
    keterampilan: Optional[str] = None
    kepribadian: Optional[str] = None
    target_karir: Optional[str] = None
    gaya_belajar: Optional[str] = None
    waktu_luang: Optional[str] = None
    universitas: Optional[str] = None
    jurusan: Optional[str] = None
    semester_sekarang: Optional[str] = None
    calendar_name: Optional[str] = "My Campus"
    picture: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    nama: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None

class User(UserBase):
    id_user: int
    model_config = ConfigDict(from_attributes=True)

# --- Auth Schemas ---
class UserRegister(BaseModel):
    nama: str
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# RAGSEmbedding Schemas
class RAGSEmbeddingBase(BaseModel):
    id_user: Optional[int] = None
    source_type: str
    source_id: Optional[str] = None
    text_original: str

class RAGSEmbeddingCreate(RAGSEmbeddingBase):
    pass

class RAGSEmbedding(RAGSEmbeddingBase):
    id_embedding: int
    embedding: List[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

# AI Chat History Schemas
class AIChatHistoryBase(BaseModel):
    id_user: int
    role: str
    message: str

class AIChatHistoryCreate(AIChatHistoryBase):
    pass

class AIChatHistory(AIChatHistoryBase):
    id_chat: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Request body for /rag/query
class RAGQuery(BaseModel):
    id_user: Optional[int] = None
    question: str
    top_k: int = 5
    client_local_time: Optional[datetime] = None

# Response for /rag/query
class RAGResponse(BaseModel):
    answer: str
    context_docs: List[RAGSEmbedding]

# Google Calendar Integration (kept for compatibility)
class CalendarEventCreate(BaseModel):
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


# Todo Schemas
class TodoBase(BaseModel):
    id_user: int
    nama: str
    tipe: str
    tenggat: Optional[datetime] = None
    deskripsi: Optional[str] = None
    id_roadmap_step: Optional[int] = None
    is_completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    id_user: Optional[int] = None
    nama: Optional[str] = None
    tipe: Optional[str] = None
    tenggat: Optional[datetime] = None
    deskripsi: Optional[str] = None
    id_roadmap_step: Optional[int] = None
    is_completed: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class Todo(TodoBase):
    id_todo: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Semester Schemas
class SemesterBase(BaseModel):
    id_user: int
    tipe: str
    tahun_ajaran: str
    tanggal_mulai: date
    tanggal_selesai: date

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(SemesterBase):
    id_user: Optional[int] = None
    tipe: Optional[str] = None
    tahun_ajaran: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None

class Semester(SemesterBase):
    id_semester: int
    google_calendar_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# JadwalMatkul Schemas
class JadwalMatkulBase(BaseModel):
    id_user: int
    id_semester: Optional[int] = None
    hari: str
    nama: str
    jam_mulai: time
    jam_selesai: time
    sks: int

class JadwalMatkulCreate(JadwalMatkulBase):
    pass

class JadwalMatkulUpdate(JadwalMatkulBase):
    id_user: Optional[int] = None
    id_semester: Optional[int] = None
    hari: Optional[str] = None
    nama: Optional[str] = None
    jam_mulai: Optional[time] = None
    jam_selesai: Optional[time] = None
    sks: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class JadwalMatkul(JadwalMatkulBase):
    id_jadwal: int
    google_event_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# UKM Schemas
class UKMBase(BaseModel):
    id_user: int
    nama: str
    jabatan: str
    deskripsi: Optional[str] = None

class UKMCreate(UKMBase):
    pass

class UKMUpdate(UKMBase):
    id_user: Optional[int] = None
    nama: Optional[str] = None
    jabatan: Optional[str] = None
    deskripsi: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UKM(UKMBase):
    id_ukm: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Rutinitas Schemas
class RutinitasBase(BaseModel):
    id_user: int
    nama: str
    hari: str
    jam_mulai: Optional[time] = None
    jam_selesai: Optional[time] = None
    deskripsi: Optional[str] = None

class RutinitasCreate(RutinitasBase):
    pass

class RutinitasUpdate(RutinitasBase):
    id_user: Optional[int] = None
    nama: Optional[str] = None
    hari: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Rutinitas(RutinitasBase):
    id_rutinitas: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AI Career Schemas ---

class CareerResultBase(BaseModel):
    career_name: str
    reason: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None

class CareerResultCreate(CareerResultBase):
    id_user: int

class CareerResult(CareerResultBase):
    id: int
    id_user: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RoadmapBase(BaseModel):
    title: str

class RoadmapCreate(RoadmapBase):
    id_user: int
    id_career: int

class Roadmap(RoadmapBase):
    id: int
    id_user: int
    id_career: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RoadmapStepBase(BaseModel):
    phase: str
    step_order: int
    title: str
    description: Optional[str] = None

class RoadmapStep(RoadmapStepBase):
    id: int
    id_roadmap: int
    skill_tags: Optional[str] = None
    xp_reward: Optional[int] = 10
    model_config = ConfigDict(from_attributes=True)

class CareerProgressBase(BaseModel):
    status: str = "pending"
    completed_at: Optional[datetime] = None

class CareerProgressCreate(CareerProgressBase):
    id_user: int
    id_roadmap_step: int

class CareerProgressUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

class CareerProgress(CareerProgressBase):
    id: int
    id_user: int
    id_roadmap_step: int
    model_config = ConfigDict(from_attributes=True)


# --- Gamification / Skill Gap Schemas ---

class SkillXPResponse(BaseModel):
    skill_name: str
    xp_points: int
    level: int
    model_config = ConfigDict(from_attributes=True)

class SkillGapItem(BaseModel):
    skill: str
    current_xp: int
    level_name: str
    next_level_name: str
    progress_pct: float # Progress within current level level
    next_level_xp: int
    needed_steps: int

class SkillGapResponse(BaseModel):
    target_karir: str
    skills: List[SkillGapItem]

# --- Adaptive Roadmap Schemas ---

class RoadmapStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skill_tags: Optional[str] = None
    xp_reward: Optional[int] = None
    phase: Optional[str] = None
    step_order: Optional[int] = None

class RoadmapStepCreate(BaseModel):
    id_roadmap: int
    phase: str
    step_order: int
    title: str
    description: Optional[str] = None
    skill_tags: Optional[str] = None
    xp_reward: int = 10

class AdaptRoadmapRequest(BaseModel):
    user_message: str

class AdaptedStep(BaseModel):
    id: Optional[int] = None
    action: str
    phase: Optional[str] = None
    step_order: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    skill_tags: Optional[str] = None
    xp_reward: Optional[int] = None

class AdaptRoadmapPreview(BaseModel):
    ai_message: str
    proposed_changes: List[AdaptedStep]

class XPGrantResponse(BaseModel):
    message: str
    xp_granted: int
    skills_updated: List[SkillXPResponse]
    profile_updated: bool = False

# Request body for activity
class ActivityCreate(RAGSEmbeddingBase):
    pass