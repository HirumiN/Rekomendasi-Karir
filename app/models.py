from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Time, Date, Boolean, Enum as SAEnum
import enum

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .db import Base


# ==========================
# USER
# ==========================

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    telepon = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    lokasi = Column(String, nullable=True)
    umur = Column(Integer, nullable=True)
    minat = Column(Text, nullable=True)
    keterampilan = Column(Text, nullable=True)
    kepribadian = Column(Text, nullable=True)
    target_karir = Column(Text, nullable=True)
    gaya_belajar = Column(Text, nullable=True)
    waktu_luang = Column(Text, nullable=True)
    
    # Academic Profile
    universitas = Column(String, nullable=True)
    jurusan = Column(String, nullable=True)
    semester_sekarang = Column(String, nullable=True)

    # Profile picture (optional, uploaded manually)
    picture = Column(String, nullable=True)
    
    # Customization
    calendar_name = Column(String, nullable=True, default="My Campus")

    # RELATIONSHIPS
    rags_embeddings = relationship("RAGSEmbedding", back_populates="owner", cascade="all, delete-orphan")
    chat_history = relationship("AIChatHistory", back_populates="owner", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    jadwal_matkul = relationship("JadwalMatkul", back_populates="owner", cascade="all, delete-orphan")
    ukm = relationship("UKM", back_populates="owner", cascade="all, delete-orphan")
    semesters = relationship("Semester", back_populates="owner", cascade="all, delete-orphan")
    rutinitas = relationship("Rutinitas", back_populates="owner", cascade="all, delete-orphan")

    # Career Features
    career_results = relationship("CareerResult", back_populates="owner", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="owner", cascade="all, delete-orphan")
    career_progress = relationship("CareerProgress", back_populates="owner", cascade="all, delete-orphan")
    skill_xp = relationship("UserSkillXP", back_populates="owner", cascade="all, delete-orphan")

# ==========================
# RAGS EMBEDDING
# ==========================

class RAGSEmbedding(Base):
    __tablename__ = "rags_embeddings"

    id_embedding = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=True)

    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=True)
    text_original = Column(Text, nullable=False)

    embedding = Column(Vector(768))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="rags_embeddings")


# ==========================
# CHAT HISTORY
# ==========================

class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    id_chat = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    role = Column(String, nullable=False)  # user / assistant
    message = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="chat_history")


# ==========================
# TODO
# ==========================

class Todo(Base):
    __tablename__ = "todos"

    id_todo = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    nama = Column(String, nullable=False)
    tipe = Column(String, nullable=False)
    tenggat = Column(DateTime, nullable=True)
    deskripsi = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)

    # Roadmap Linking
    id_roadmap_step = Column(Integer, ForeignKey("roadmap_steps.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="todos")
    roadmap_step = relationship("RoadmapStep", back_populates="todos")


# ==========================
# SEMESTER
# ==========================

class Semester(Base):
    __tablename__ = "semesters"

    id_semester = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))
    
    tipe = Column(String, nullable=False)
    tahun_ajaran = Column(String, nullable=False)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_selesai = Column(Date, nullable=False)
    
    owner = relationship("User", back_populates="semesters")
    jadwal_matkul = relationship("JadwalMatkul", back_populates="semester", cascade="all, delete-orphan")


# ==========================
# JADWAL MATA KULIAH
# ==========================

class HariEnum(str, enum.Enum):
    Senin = "Senin"
    Selasa = "Selasa"
    Rabu = "Rabu"
    Kamis = "Kamis"
    Jumat = "Jumat"
    Sabtu = "Sabtu"
    Minggu = "Minggu"

class JadwalMatkul(Base):
    __tablename__ = "jadwal_matkul"

    id_jadwal = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))
    id_semester = Column(Integer, ForeignKey("semesters.id_semester"), nullable=True)

    hari = Column(SAEnum(HariEnum), nullable=True)
    nama = Column(String, nullable=False)
    jam_mulai = Column(Time, nullable=True)
    jam_selesai = Column(Time, nullable=True)
    sks = Column(Integer, nullable=False)
    semester_level = Column(Integer, nullable=True) # 1-8

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="jadwal_matkul")
    semester = relationship("Semester", back_populates="jadwal_matkul")


# ==========================
# UKM
# ==========================

class UKM(Base):
    __tablename__ = "ukm"

    id_ukm = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    nama = Column(String, nullable=False)
    jabatan = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="ukm")


# ==========================
# CAREER RESULTS
# ==========================

class CareerResult(Base):
    __tablename__ = "career_results"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    career_name = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="career_results")
    roadmaps = relationship("Roadmap", back_populates="career_result", cascade="all, delete-orphan")


# ==========================
# ROADMAPS
# ==========================

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_career = Column(Integer, ForeignKey("career_results.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="roadmaps")
    career_result = relationship("CareerResult", back_populates="roadmaps")
    steps = relationship("RoadmapStep", back_populates="roadmap", cascade="all, delete-orphan")


# ==========================
# ROADMAP STEPS
# ==========================

class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(Integer, primary_key=True, index=True)
    id_roadmap = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    phase = Column(String, nullable=False)
    step_order = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    skill_tags = Column(Text, nullable=True)  # JSON: ["Python","ML"]
    xp_reward = Column(Integer, default=10)

    roadmap = relationship("Roadmap", back_populates="steps")
    todos = relationship("Todo", back_populates="roadmap_step")
    progress = relationship("CareerProgress", back_populates="roadmap_step", cascade="all, delete-orphan")


# ==========================
# CAREER PROGRESS
# ==========================

class CareerProgress(Base):
    __tablename__ = "career_progress"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_roadmap_step = Column(Integer, ForeignKey("roadmap_steps.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="pending")
    completed_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="career_progress")
    roadmap_step = relationship("RoadmapStep", back_populates="progress")

# ==========================
# RUTINITAS (HABITS)
# ==========================

class Rutinitas(Base):
    __tablename__ = "rutinitas"

    id_rutinitas = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)

    nama = Column(String, nullable=False)
    hari = Column(String, nullable=False) 
    jam_mulai = Column(Time, nullable=True)
    jam_selesai = Column(Time, nullable=True)
    deskripsi = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="rutinitas")


# ==========================
# USER SKILL XP (Gamification)
# ==========================

class UserSkillXP(Base):
    __tablename__ = "user_skill_xp"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String, nullable=False)
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    owner = relationship("User", back_populates="skill_xp")


# ==========================
# CURRICULUM SYSTEM
# ==========================

class Campus(Base):
    __tablename__ = "campuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    departments = relationship("Department", back_populates="campus", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    name = Column(String, nullable=False)
    
    campus = relationship("Campus", back_populates="departments")
    curricula = relationship("Curriculum", back_populates="department", cascade="all, delete-orphan")


class Curriculum(Base):
    __tablename__ = "curricula"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester = Column(String, nullable=True) # e.g. "Ganjil" or "Genap"
    
    department = relationship("Department", back_populates="curricula")
    courses = relationship("Course", back_populates="curriculum", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer, ForeignKey("curricula.id"), nullable=False)
    
    name = Column(String, nullable=False)
    sks = Column(Integer, nullable=False)
    semester_target = Column(Integer, nullable=False)
    is_elective = Column(Boolean, default=False)
    
    curriculum = relationship("Curriculum", back_populates="courses")