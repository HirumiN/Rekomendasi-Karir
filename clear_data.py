from sqlalchemy import text
from app.db import SessionLocal

db = SessionLocal()
try:
    print("Clearing roadmaps and todos...")
    db.execute(text("DELETE FROM todos;"))
    db.execute(text("DELETE FROM career_progress;"))
    db.execute(text("DELETE FROM roadmap_steps;"))
    db.execute(text("DELETE FROM roadmaps;"))
    db.execute(text("DELETE FROM career_results;"))
    db.commit()
    print("Successfully wiped Todos and Roadmaps.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
