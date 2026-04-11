from app import db, models

def seed():
    session = db.SessionLocal()
    try:
        # Check if campuses already exist
        if session.query(models.Campus).first():
            print("Database already has campuses.")
            return

        campuses_data = [
            {
                "name": "Politeknik Perkapalan Negeri Surabaya",
                "departments": ["Teknik Informatika", "Sistem Informasi", "Teknik Perkapalan", "Teknik Permesinan Kapal"]
            },
            {
                "name": "Politeknik Elektronika Negeri Surabaya",
                "departments": ["Teknik Informatika", "Teknik Komputer", "Sistem Pembangkit Energi", "Teknik Mekatronika"]
            },
            {
                "name": "Universitas Airlangga",
                "departments": ["Kedokteran", "Hukum", "Sains dan Teknologi", "Ilmu Komputer", "Sistem Informasi"]
            },
            {
                "name": "Institut Teknologi Sepuluh Nopember",
                "departments": ["Teknik Informatika", "Sistem Informasi", "Teknik Sipil", "Teknik Elektro"]
            }
        ]

        for campus_info in campuses_data:
            campus = models.Campus(name=campus_info["name"])
            session.add(campus)
            session.flush() # Get campus ID
            
            for dept_name in campus_info["departments"]:
                dept = models.Department(campus_id=campus.id, name=dept_name)
                session.add(dept)
        
        session.commit()
        print("Successfully seeded campuses and departments.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
