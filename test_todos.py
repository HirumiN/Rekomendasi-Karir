from app.db import SessionLocal
from app import crud

db = SessionLocal()
try:
    print("Testing get_todos_by_user...")
    todos = crud.get_todos_by_user(db, 2)
    print(f"Success! Found {len(todos)} todos.")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
