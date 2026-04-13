import asyncio
from sqlalchemy import create_engine, text
import datetime

DATABASE_URL = "postgresql+psycopg://root:12345678@localhost:5432/aicareer"
USER_ID = 11

def seed_planner():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print(f"Seeding data for user_id: {USER_ID}")
        
        # 1. Update Jadwal Matkul (Pick some and give them time/day)
        # We'll pick specific IDs or just update by name for this user
        schedules = [
            {"nama": "Elektronika Digital 1", "hari": "Senin", "mulai": "08:00", "selesai": "10:30", "sks": 3},
            {"nama": "Agama", "hari": "Senin", "mulai": "13:00", "selesai": "14:40", "sks": 2},
            {"nama": "Matematika Teknik 2", "hari": "Selasa", "mulai": "08:00", "selesai": "10:30", "sks": 3},
            {"nama": "Rangkaian Listrik", "hari": "Selasa", "mulai": "11:00", "selesai": "13:30", "sks": 3},
            {"nama": "Pemrograman Komputer", "hari": "Rabu", "mulai": "09:00", "selesai": "11:30", "sks": 3},
            {"nama": "Fisika Teknik", "hari": "Kamis", "mulai": "10:00", "selesai": "12:30", "sks": 3},
            {"nama": "Bahasa Inggris Profesional", "hari": "Jumat", "mulai": "08:00", "selesai": "09:40", "sks": 2},
        ]

        # Reset old schedule logic for this user to make it clean
        # conn.execute(text(f"UPDATE jadwal_matkul SET hari = NULL, jam_mulai = NULL, jam_selesai = NULL WHERE id_user = {USER_ID}"))
        
        for s in schedules:
            conn.execute(text("""
                UPDATE jadwal_matkul 
                SET hari = :hari, jam_mulai = :mulai, jam_selesai = :selesai
                WHERE id_user = :id_user AND nama ILIKE :nama
            """), {
                "hari": s["hari"], 
                "mulai": s["mulai"], 
                "selesai": s["selesai"], 
                "id_user": USER_ID, 
                "nama": f"%{s['nama']}%"
            })
        print("Schedule updated with times.")

        # 2. Seed Todos
        todos = [
            {"nama": "Review Materi Elektronika Digital", "deskripsi": "Pelajari gerbang logika dasar dan flip-flop", "tipe": "Tinggi", "tenggat": "2026-04-15 10:00:00"},
            {"nama": "Kerjakan Tugas Matematika Teknik", "deskripsi": "Latihan soal transformasi Laplace", "tipe": "Tinggi", "tenggat": "2026-04-14 23:59:00"},
            {"nama": "Install Python & VS Code", "deskripsi": "Persiapan untuk mata kuliah Pemrograman", "tipe": "Menengah", "tenggat": "2026-04-14 12:00:00"},
            {"nama": "Beli Komponen Breadboard", "deskripsi": "Cari di toko online atau pasar lokal", "tipe": "Rendah", "tenggat": "2026-04-17 17:00:00"},
            {"nama": "Update CV di LinkedIn", "deskripsi": "Tambahkan skill baru yang dipelajari", "tipe": "Menengah", "tenggat": "2026-04-20 09:00:00"},
        ]
        
        for t in todos:
            conn.execute(text("""
                INSERT INTO todos (id_user, nama, deskripsi, tipe, tenggat, is_completed)
                VALUES (:id_user, :nama, :deskripsi, :tipe, :tenggat, false)
            """), {**t, "id_user": USER_ID})
        print("Todos seeded.")

        # 3. Seed Rutinitas
        rutinitas = [
            {"nama": "Olahraga Pagi", "hari": "Setiap Hari", "jam_mulai": "05:30", "jam_selesai": "06:30", "deskripsi": "Jogging atau stretching ringan"},
            {"nama": "Deep Work: Belajar Karir", "hari": "Setiap Hari", "jam_mulai": "20:00", "jam_selesai": "22:00", "deskripsi": "Fokus belajar skill yang dibutuhkan untuk target karir"},
            {"nama": "Revisi Proyek Akhir", "hari": "Sabtu", "jam_mulai": "09:00", "jam_selesai": "12:00", "deskripsi": "Progress report harian"},
            {"nama": "Me Time / Istirahat", "hari": "Minggu", "jam_mulai": "13:00", "jam_selesai": "16:00", "deskripsi": "Nonton film atau baca buku non-teknis"},
        ]

        for r in rutinitas:
            conn.execute(text("""
                INSERT INTO rutinitas (id_user, nama, hari, jam_mulai, jam_selesai, deskripsi)
                VALUES (:id_user, :nama, :hari, :jam_mulai, :jam_selesai, :deskripsi)
            """), {**r, "id_user": USER_ID})
        print("Rutinitas seeded.")
        
        conn.commit()
        print("All data committed successfully.")

if __name__ == "__main__":
    seed_planner()
