import asyncio
import os
import sys
import time
import httpx
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Ensure this script runs inside the app directory appropriately
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app import models, schemas, crud, rag, rag_service

BASE_URL = "http://localhost:8000"

async def test_roadmap_multi_trial(user_id, n=3):
    print(f"\n--- Running Roadmap Multi-Trial (n={n}) ---")
    db = SessionLocal()
    results = []
    try:
        for i in range(n):
            try:
                start_time = time.time()
                analysis = await rag.generate_career_analysis(db, user_id)
                duration = time.time() - start_time
                tokens = len(json.dumps(analysis)) // 4
                steps = sum(len(p.get('steps', [])) for p in analysis.get('roadmap', []))
                print(f"  Trial {i+1}: {duration:.2f}s | {steps} steps | ~{tokens} tokens")
                results.append({"duration": duration, "steps": steps, "tokens": tokens, "status": "Success"})
            except Exception as e:
                print(f"  Trial {i+1}: Failed ({e})")
                results.append({"duration": 0, "steps": 0, "tokens": 0, "status": f"Failed ({type(e).__name__})"})
            await asyncio.sleep(2) # Increased gap
    finally:
        db.close()
    return results

async def test_high_concurrency(n_list=[10, 20]):
    print(f"\n--- Running High Concurrency Tests ---")
    payload = {"question": "Apa rencana saya hari ini?", "id_user": 1, "top_k": 3}
    concurrency_results = {}

    async with httpx.AsyncClient(timeout=60.0) as client:
        for n in n_list:
            print(f"Testing concurrency for n={n}...")
            start_time = time.time()
            tasks = [client.post(f"{BASE_URL}/rag/query", json=payload) for _ in range(n)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            success_durations = []
            failed_count = 0
            for r in responses:
                if isinstance(r, httpx.Response) and r.status_code == 200:
                    success_durations.append(r.elapsed.total_seconds())
                else:
                    failed_count += 1
            
            avg_dur = sum(success_durations) / len(success_durations) if success_durations else 0
            total_dur = end_time - start_time
            print(f"  n={n}: Batch={total_dur:.2f}s | Avg={avg_dur:.2f}s | Failed={failed_count}")
            concurrency_results[n] = {"total": total_dur, "avg": avg_dur, "failed": failed_count}
            await asyncio.sleep(5) # Cooldown
            
    return concurrency_results

async def test_comparison(user_id):
    print("\n--- Running Comparison: Consultation vs Roadmap ---")
    db = SessionLocal()
    
    # 1. Normal Consultation
    print("Testing Normal Consultation...")
    payload = {"question": "Bantu saya merencanakan hari ini.", "id_user": user_id, "top_k": 5}
    async with httpx.AsyncClient(timeout=30.0) as client:
        start_time = time.time()
        res_cons = await client.post(f"{BASE_URL}/rag/query", json=payload)
        dur_cons = time.time() - start_time
        tokens_cons = len(res_cons.text) // 4
    
    # 2. Roadmap Generation
    print("Testing Roadmap Generation...")
    start_time = time.time()
    try:
        analysis = await rag.generate_career_analysis(db, user_id)
        dur_road = time.time() - start_time
        tokens_road = len(json.dumps(analysis)) // 4
    except:
        dur_road, tokens_road = 0, 0
    
    db.close()
    return {
        "consultation": {"dur": dur_cons, "tokens": tokens_cons},
        "roadmap": {"dur": dur_road, "tokens": tokens_road}
    }

async def run_comprehensive_trials():
    db = SessionLocal()
    user = db.query(models.User).first()
    user_id = user.id_user if user else 1
    db.close()

    roadmap_multi = await test_roadmap_multi_trial(user_id, n=3)
    concurrency_high = await test_high_concurrency(n_list=[10, 20])
    comparison = await test_comparison(user_id)
    
    print("\n--- FINAL SUMMARY FOR METHODOLOGY ---")
    print(f"Multi-Roadmap Trials: {[r['status'] for r in roadmap_multi]}")
    for n, data in concurrency_high.items():
        print(f"Concurrency @{n}: Batch={data['total']:.2f}s | Avg={data['avg']:.2f}s | Failed={data['failed']}")
    print(f"Comparison: Cons={comparison['consultation']['dur']:.2f}s ({comparison['consultation']['tokens']} tks) vs Roadmap={comparison['roadmap']['dur']:.2f}s ({comparison['roadmap']['tokens']} tks)")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_trials())
