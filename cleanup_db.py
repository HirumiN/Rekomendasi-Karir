from app.db import SessionLocal
from app import models

def cleanup():
    db = SessionLocal()
    try:
        print("Cleaning up roadmap and todo data...")
        
        # Order matters if no cascade, but we have cascade in models.
        # To be safe, we can just delete from main tables.
        
        # 1. Delete Todos
        num_todos = db.query(models.Todo).delete()
        print(f"Deleted {num_todos} todos.")
        
        # 2. Delete Career Results (will cascade to Roadmaps -> Steps -> Progress)
        num_careers = db.query(models.CareerResult).delete()
        print(f"Deleted {num_careers} career results.")
        
        # 3. Delete Roadmaps (in case some aren't linked to career_results)
        num_rd = db.query(models.Roadmap).delete()
        print(f"Deleted {num_rd} roadmaps.")
        
        # 4. Delete Skill XP
        num_xp = db.query(models.UserSkillXP).delete()
        print(f"Deleted {num_xp} skill XP entries.")
        
        db.commit()
        print("Cleanup completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
