import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db import SessionLocal
from app import models

db = SessionLocal()
try:
    deleted_count = db.query(models.User).delete()
    db.commit()
    print(f"Beres! Menghapus {deleted_count} user dan semua data relasinya (cascade).")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
