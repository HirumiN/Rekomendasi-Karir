import asyncio
import os
import sys
import time
import httpx
import json
import csv
from datetime import datetime
from sqlalchemy.orm import Session

# Ensure this script runs inside the app directory appropriately
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app import models, schemas, crud, rag, rag_service

BASE_URL = "http://localhost:8000"

async def seed_curriculum():
    print("--- Seeding Curriculum Directly ---")
    db = SessionLocal()
    try:
        csv_path = "/home/hirumi/Documents/TAAI/fastapi-simple-rag/kurikulum_pens.csv"
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for item in reader:
                # 1. Campus
                campus = db.query(models.Campus).filter(models.Campus.name == item["universitas"]).first()
                if not campus:
                    campus = models.Campus(name=item["universitas"])
                    db.add(campus); db.commit(); db.refresh(campus)
                
                # 2. Department
                dept = db.query(models.Department).filter(models.Department.name == item["jurusan"], models.Department.campus_id == campus.id).first()
                if not dept:
                    dept = models.Department(campus_id=campus.id, name=item["jurusan"])
                    db.add(dept); db.commit(); db.refresh(dept)
                
                # 3. Curriculum
                curr_semester = item.get("semester")
                curr = db.query(models.Curriculum).filter(models.Curriculum.department_id == dept.id, models.Curriculum.semester == curr_semester).first()
                if not curr:
                    curr = models.Curriculum(department_id=dept.id, semester=curr_semester)
                    db.add(curr); db.commit(); db.refresh(curr)
                
                # 4. Course
                exists = db.query(models.Course).filter(models.Course.kurikulum_id == curr.id, models.Course.nama_mk == item["nama_mk"]).first()
                if not exists:
                    course = models.Course(
                        kurikulum_id=curr.id,
                        kode_mk=item["kode_mk"],
                        nama_mk=item["nama_mk"],
                        sks=int(item["sks"]),
                        semester=int(item["semester"]),
                        kategori=item["kategori"]
                    )
                    db.add(course); db.commit()
        print("Success: Curriculum seeded.")
    except Exception as e:
        print(f"Seed Error: {e}")
    finally:
        db.close()

async def test_roadmap_generation(user_id):
    print("\n--- Testing Roadmap Generation ---")
    db = SessionLocal()
    try:
        start_time = time.time()
        analysis = await rag.generate_career_analysis(db, user_id)
        duration = time.time() - start_time
        
        print(f"Roadmap Duration: {duration:.2f}s")
        print(f"Careers Suggested: {len(analysis.get('careers', []))}")
        print(f"Roadmap Phases: {len(analysis.get('roadmap', []))}")
        
        # Token estimation (Approx 4 chars per token)
        prompt_len = len(str(analysis)) # This is response, not prompt, but let's estimate
        print(f"Estimated Response Tokens: ~{len(json.dumps(analysis)) // 4}")
        
        return {
            "duration": duration,
            "careers": len(analysis.get('careers', [])),
            "steps": sum(len(p.get('steps', [])) for p in analysis.get('roadmap', []))
        }
    finally:
        db.close()

async def test_concurrency(n=5):
    print(f"\n--- Testing Concurrency (n={n}) ---")
    payload = {"question": "Apa jadwal saya?", "id_user": 1, "top_k": 3}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        start_time = time.time()
        tasks = [client.post(f"{BASE_URL}/rag/query", json=payload) for _ in range(n)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
    durations = [r.elapsed.total_seconds() for r in responses]
    avg_dur = sum(durations) / len(durations)
    total_dur = end_time - start_time
    
    print(f"Concurrent Batch Total: {total_dur:.2f}s")
    print(f"Individual Avg Duration: {avg_dur:.2f}s")
    return {"total": total_dur, "avg": avg_dur}

async def run_advanced_trials():
    await seed_curriculum()
    
    db = SessionLocal()
    user = db.query(models.User).first()
    user_id = user.id_user if user else 1
    db.close()

    roadmap_res = await test_roadmap_generation(user_id)
    concurrency_res = await test_concurrency(n=5)
    
    print("\n--- Summary for Advanced Methodology ---")
    print(f"Roadmap Gen: {roadmap_res['duration']:.2f}s | {roadmap_res['steps']} steps")
    print(f"Concurrency @5: Batch={concurrency_res['total']:.2f}s | Avg={concurrency_res['avg']:.2f}s")

if __name__ == "__main__":
    asyncio.run(run_advanced_trials())
