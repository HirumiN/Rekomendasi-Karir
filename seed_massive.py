import asyncio
import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

# Ensure this script runs inside the app directory appropriately
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app import models, schemas, crud, rag_service

async def main():
    db = SessionLocal()
    try:
        user = db.query(models.User).first()
        if not user:
            print("No user found. Please run seed_dummy.py first.")
            return

        print(f"--- Seeding MASSIVE data for user {user.nama} ---")
        
        # Add 50 Todos
        print("Adding 50 Todos...")
        for i in range(50):
            t = schemas.TodoCreate(
                id_user=user.id_user,
                nama=f"Tugas Rutin ke-{i+1}",
                tipe=random.choice(["Tinggi", "Menengah", "Rendah"]),
                tenggat=datetime.now() + timedelta(days=random.randint(1, 30)),
                deskripsi=f"Deskripsi detail untuk tugas ke-{i+1} agar embedding memiliki teks yang bervariasi."
            )
            db_t = crud.create_todo(db, t)
            await rag_service.update_todo_embedding(db, db_t)
            if i % 10 == 0:
                print(f"  Processed {i} todos...")

        # Add 20 Schedules
        print("Adding 20 more Schedules...")
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        for i in range(20):
            j = schemas.JadwalMatkulCreate(
                id_user=user.id_user,
                hari=random.choice(days),
                nama=f"Mata Kuliah Pilihan {i+1}",
                jam_mulai=f"{random.randint(7, 16):02d}:00:00",
                jam_selesai=f"{random.randint(17, 21):02d}:00:00",
                sks=random.randint(2, 4),
                semester_level=random.randint(1, 8)
            )
            db_j = crud.create_jadwal_matkul(db, j)
            # Embedding handled in crud for jadwal usually, but let's be sure if needed
        
        print("--- Massive Seeding Complete! ---")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
