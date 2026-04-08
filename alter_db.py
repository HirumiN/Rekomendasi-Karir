import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("ALTER TABLE users ADD COLUMN universitas VARCHAR;"))
    db.execute(text("ALTER TABLE users ADD COLUMN jurusan VARCHAR;"))
    db.execute(text("ALTER TABLE users ADD COLUMN semester_sekarang VARCHAR;"))
    db.commit()
    print("Columns added successfully!")
except Exception as e:
    print(f"Error (maybe already exists?): {e}")
    db.rollback()
