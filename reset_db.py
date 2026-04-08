import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db import engine, Base
from app import models

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Database has been reset successfully.")
