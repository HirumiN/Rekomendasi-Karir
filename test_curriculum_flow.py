import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app import models, schemas, crud
import csv

def test_flow():
    db = SessionLocal()
    
    print("Step 1: Resetting Database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("Step 2: Creating User...")
    user_in = schemas.UserCreate(
        nama="Hirumi",
        email="hirumi@example.com",
        username="hirumi"
    )
    user = crud.create_user(db, user_in)
    
    print("Step 3: Importing Curriculum from CSV...")
    csv_file = "kurikulum_pens.csv"
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Simulate API import logic
    for item in data:
        campus = crud.get_campus_by_name(db, item["universitas"])
        if not campus:
            campus = crud.create_campus(db, schemas.CampusCreate(name=item["universitas"]))
        
        dept = crud.get_department_by_name_and_campus(db, item["jurusan"], campus.id)
        if not dept:
            dept = crud.create_department(db, schemas.DepartmentCreate(campus_id=campus.id, name=item["jurusan"]))
        
        curr = crud.get_curriculum_by_name_and_dept(db, item["kurikulum"], dept.id)
        if not curr:
            curr = crud.create_curriculum(db, schemas.CurriculumCreate(
                department_id=dept.id, 
                name=item["kurikulum"], 
                year=int(item["tahun"])
            ))
        
        crud.create_course(db, schemas.CourseCreate(
            curriculum_id=curr.id,
            code=item["kode_mk"],
            name=item["nama_mk"],
            sks=int(item["sks"]),
            semester_target=int(item["semester"]),
            is_elective=(item.get("kategori", "").lower() == "pilihan")
        ))
    
    print("Step 4: User selects PENS and IT Department...")
    campus = crud.get_campus_by_name(db, "PENS")
    depts = crud.get_departments_by_campus(db, campus.id)
    target_dept = next(d for d in depts if d.name == "Teknik Informatika")
    curricula = crud.get_curricula_by_department(db, target_dept.id)
    target_curr = curricula[0]
    
    print(f"Selected: {campus.name} -> {target_dept.name} -> {target_curr.name}")
    
    print("Step 5: Creating User Semester Session...")
    semester_in = schemas.SemesterCreate(
        id_user=user.id_user,
        tipe="Ganjil",
        tahun_ajaran="2024/2025",
        tanggal_mulai="2024-09-01",
        tanggal_selesai="2025-01-31"
    )
    semester = crud.create_semester(db, semester_in)
    
    print("Step 6: Connecting Curriculum (Semester 1)...")
    results = crud.connect_curriculum_to_user(
        db, 
        user.id_user, 
        target_curr.id, 
        semester.id_semester, 
        1 # Target Semester 1
    )
    
    print(f"Success! Added {len(results)} courses to schedule.")
    for r in results:
        print(f" - {r.nama} (SKS: {r.sks}) | Day/Time: {r.hari}/{r.jam_mulai}")

    db.close()

if __name__ == "__main__":
    test_flow()
