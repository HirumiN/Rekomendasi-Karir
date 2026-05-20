import sys
import os
import asyncio
import json

# Add current dir to path
sys.path.append(os.getcwd())

from app.db import SessionLocal
from app import models
from app.rag import generate_career_analysis

async def run():
    db = SessionLocal()
    # Find any user
    user = db.query(models.User).first()
    if not user:
        print("No users found")
        return
    
    print(f"Testing for user: {user.nama}")
    
    # We will test the roadmap generation
    res = await generate_career_analysis(db, user.id_user)
    
    roadmap = res.get("roadmap", [])
    for phase in roadmap:
        print(f"Phase: {phase.get('phase')}")
        for step in phase.get("steps", []):
            tags = step.get("skill_tags", [])
            print(f"  Step: {step.get('title')}")
            print(f"    Type of tags: {type(tags)}")
            print(f"    Tags: {tags}")

if __name__ == "__main__":
    asyncio.run(run())
