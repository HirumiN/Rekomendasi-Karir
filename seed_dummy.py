import asyncio
import os
import sys

# Ensure this script runs inside the app directory appropriately
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models, schemas, crud, rag_service
from datetime import date, time, datetime, timedelta

async def main():
    db = SessionLocal()
    try:
        # Get or create the first user
        user = db.query(models.User).first()
        if not user:
            print("Creating default test user...")
            user = models.User(
                nama="Hirumi", 
                username="hirumi", 
                email="hirumi@example.com",
                password_hash="password123", # Standard for dummy
                semester_sekarang="4",
                universitas="Institut Teknologi Sepuluh Nopember",
                jurusan="Teknik Informatika"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        print(f"Adding massive dummy data for user: {user.nama} (ID: {user.id_user})")
        
        # 1. Update user profile to reflect a very busy student
        user_update = schemas.UserUpdate(
            umur=21,
            target_karir="Software Engineer / AI Researcher",
            minat="Programming, Machine Learning, Open Source, Menulis Blog, Olahraga Lari",
            keterampilan="Python, JavaScript, React, SQL, Project Management",
            kepribadian="Pemikir Logis, Analitis, Kadang prokrastinasi kalau tugasnya mudah, tapi sangat kompetitif.",
            gaya_belajar="Visual (Membaca Dokumentasi/Video), Kinestetik (Langsung ngoding), Suka belajar malam hari (Night Owl).",
            waktu_luang="Sangat padat. Waktu luang biasanya setelah jam 9 malam atau di hari Minggu pagi."
        )
        crud.update_user(db, user.id_user, user_update)
        # Refresh user so updates are pulled
        user = db.query(models.User).filter_by(id_user=user.id_user).first()
        await rag_service.update_user_embedding(db, user)
        print("- User profile updated & embedded for RAG.")
        
        print("- User profile updated.")
        
        # 2. Skip Semester creation (we use semester_level now)
        now = datetime.now()
        
        # 3. Add Jadwal Matkul (6 Mata Kuliah)
        jadwals = [
            ("Senin", "Kecerdasan Buatan (AI)", time(8, 0, 0), time(10, 30, 0), 3),
            ("Senin", "Proyek Perangkat Lunak", time(13, 0, 0), time(15, 30, 0), 3),
            ("Selasa", "Machine Learning", time(9, 0, 0), time(11, 30, 0), 3),
            ("Rabu", "Etika Profesi IT", time(10, 0, 0), time(11, 40, 0), 2),
            ("Kamis", "Pemrograman Web Lanjut", time(13, 0, 0), time(15, 30, 0), 3),
            ("Jumat", "Cloud Computing", time(8, 0, 0), time(10, 30, 0), 3),
        ]
        
        for hari, nama, start, end, sks in jadwals:
            j = schemas.JadwalMatkulCreate(
                id_user=user.id_user, 
                hari=hari, 
                nama=nama, 
                jam_mulai=start, 
                jam_selesai=end, 
                sks=sks,
                semester_level=int(user.semester_sekarang or 1)
            )
            db_j = crud.create_jadwal_matkul(db, j)
        print(f"- {len(jadwals)} Jadwal Matkul added & embedded.")
        
        # 4. Add Todos (10 Various Tasks with proper priority tags)
        todos = [
            ("Tugas Besar AI - Klasifikasi Gambar", "Tinggi", 7, "Buat model CNN dengan PyTorch. Target akurasi 90%."),
            ("Kuis Machine Learning", "Tinggi", 2, "Pelajari materi SVM dan Decision Tree dari slide minggu 3-4."),
            ("Rapat Evaluasi Program Kerja BEM (Deadline Draft)", "Menengah", 1, "Bawa laporan LPJ divisi Kominfo."),
            ("Review Pull Request Tim Front-end", "Menengah", 3, "Cek branch proyek RPL teman sekelompok di Github."),
            ("Belajar Dasar AWS (Cloud Computing)", "Menengah", 5, "Buat akun free tier AWS dan deploy simple web app."),
            ("Kumpul Laporan Praktikum Jaringan", "Tinggi", 2, "Submit laporan PDF ke portal e-learning."),
            ("Fixing Bug Mobile UI/UX", "Tinggi", 4, "Selesaikan isu responsive design di portofolio pribadi."),
            ("Brainstorming Ide Lomba Gemastik", "Menengah", 6, "Diskusi bareng kelompok cari problem statement IoT."),
            ("Nonton Final Turnamen Valorant", "Rendah", 1, "Santai sebentar nonton VCT sama teman-teman via Discord."),
            ("Deadline Pendaftaran Magang Tokopedia", "Tinggi", 14, "Submit CV yang sudah di-update dan lengkapi form administrasi.")
        ]
        
        for idx, (nama, tipe, plus_days, desc) in enumerate(todos):
            t = schemas.TodoCreate(
                id_user=user.id_user,
                nama=nama,
                tipe=tipe,
                tenggat=now + timedelta(days=plus_days),
                deskripsi=desc
            )
            db_t = crud.create_todo(db, t)
            await rag_service.update_todo_embedding(db, db_t)
        print(f"- {len(todos)} Todos added & embedded.")

        # 5. Add Rutinitas (Habit Items)
        rutinitas_data = [
            ("Lari Pagi 5KM di CFD / Jalan Raya", "Sabtu & Minggu", time(5, 30, 0), time(6, 30, 0), "Menjaga stamina biar nggak begadang terus."),
            ("Membaca Artikel Tech & Dokumentasi", "Setiap Hari", time(21, 0, 0), time(22, 0, 0), "Belajar stack JS terbaru."),
            ("Rapat Rutin Kadiv Kominfo BEM", "Senin", time(19, 0, 0), time(21, 0, 0), "Evaluasi progress proker BEM dengan tim divisi tiap senin malam.")
        ]
        
        for nama, hari, t_mulai, t_selesai, deskripsi in rutinitas_data:
            r = schemas.RutinitasCreate(
                id_user=user.id_user,
                nama=nama,
                hari=hari,
                jam_mulai=t_mulai,
                jam_selesai=t_selesai,
                deskripsi=deskripsi
            )
            db_r = crud.create_rutinitas(db, r)
            await rag_service.update_rutinitas_embedding(db, db_r)
        print(f"- {len(rutinitas_data)} Rutinitas added & embedded.")

        # 6. Add UKM/Organization
        ukms = [
            ("Badan Eksekutif Mahasiswa (BEM)", "Menteri Komunikasi dan Informasi", "Membawahi 3 divisi, rutin lembur menyiapkan publikasi event universitas."),
            ("Himpunan Mahasiswa Informatika (HMIF)", "Staf Divisi R&D", "Fokus memberikan pelatihan IT untuk mahasiswa baru tiap akhir pekan.")
        ]
        
        for nama, jabatan, desc in ukms:
            u = schemas.UKMCreate(
                id_user=user.id_user,
                nama=nama,
                jabatan=jabatan,
                deskripsi=desc
            )
            db_u = crud.create_ukm(db, u)
            await rag_service.update_ukm_embedding(db, db_u)
        print(f"- {len(ukms)} Organisasi/UKM added & embedded.")

        print("-----------------------------------------")
        print("✨ Sukses! Data dummy ekstensif telah berhasil diunggah!")
        print("Sekarang RAG punya konteks super padat soal kehidupan kamu.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
