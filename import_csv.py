import csv
import sys
import os
from sqlalchemy.orm import Session
from app import db, models, crud, schemas

def import_from_csv(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    session = db.SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Expected Headers: 
            # universitas, jurusan, semester_type, nama_mk, sks, semester, kategori
            
            count = 0
            for row in reader:
                try:
                    # Robust parsing to handle unescaped commas in nama_mk
                    if None in row:
                        # Reconstruct all values in order
                        values = [
                            row["universitas"], row["jurusan"], row["semester_type"], 
                            row["nama_mk"], row["sks"], row["semester"], row["kategori"]
                        ] + row[None]
                        
                        campus_name = values[0].strip()
                        dept_name = values[1].strip()
                        curr_semester = values[2].strip()
                        course_name = ",".join(values[3:-3]).strip()
                        sks_str = values[-3].strip()
                        semester_str = values[-2].strip()
                        kategori_str = values[-1].strip()
                    else:
                        campus_name = row["universitas"].strip()
                        dept_name = row["jurusan"].strip()
                        curr_semester = row.get("semester_type", row.get("semester", "Ganjil")).strip()
                        course_name = row["nama_mk"].strip()
                        sks_str = row["sks"].strip()
                        semester_str = row["semester"].strip()
                        kategori_str = row.get("kategori", "").strip()

                    # 1. Campus
                    campus = crud.get_campus_by_name(session, campus_name)
                    if not campus:
                        campus = crud.create_campus(session, schemas.CampusCreate(name=campus_name))
                        print(f"Created Campus: {campus_name}")
                    
                    # 2. Department
                    dept = crud.get_department_by_name_and_campus(session, dept_name, campus.id)
                    if not dept:
                        dept = crud.create_department(session, schemas.DepartmentCreate(campus_id=campus.id, name=dept_name))
                        print(f"Created Department: {dept_name} at {campus_name}")
                    
                    # 3. Curriculum
                    curr = crud.get_curriculum_by_dept_and_semester(session, dept.id, curr_semester)
                    if not curr:
                        curr = crud.create_curriculum(session, schemas.CurriculumCreate(
                            department_id=dept.id, 
                            semester=curr_semester
                        ))
                    
                    # 4. Course
                    try:
                        sks = int(sks_str) if sks_str else None
                    except ValueError:
                        sks = None
                    
                    try:
                        semester = int(semester_str) if semester_str else None
                    except ValueError:
                        semester = None
                        
                    is_elective = (kategori_str.lower() == "pilihan")
                    
                    # Check if course already exists in this curriculum to avoid duplicates
                    existing_course = session.query(models.Course).filter_by(
                        curriculum_id=curr.id,
                        name=course_name
                    ).first()
                    
                    if not existing_course:
                        crud.create_course(session, schemas.CourseCreate(
                            curriculum_id=curr.id,
                            name=course_name,
                            sks=sks,
                            semester_target=semester,
                            is_elective=is_elective
                        ))
                        count += 1
                
                except Exception as row_error:
                    session.rollback() # Clear the failed transaction state
                    print(f"Error processing row {row}: {row_error}")
            
            session.commit()
            print(f"Successfully imported {count} new courses.")
            
    except Exception as e:
        session.rollback()
        print(f"Critical error during import: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 import_csv.py <path_to_csv>")
    else:
        import_from_csv(sys.argv[1])
