import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("TRUNCATE TABLE users CASCADE;"))
    db.commit()
    print("ALL USERS AND RELATED TABLES HAVE BEEN TRUNCATED VIA CASCADE.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
