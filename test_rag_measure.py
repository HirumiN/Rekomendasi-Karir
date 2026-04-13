import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_query(question, id_user=None, include_time=True):
    payload = {
        "question": question,
        "top_k": 5
    }
    if id_user:
        payload["id_user"] = id_user
    if include_time:
        payload["client_local_time"] = datetime.now().isoformat()
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/rag/query", json=payload)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if response.status_code == 200:
        data = response.json()
        return {
            "status": "success",
            "duration": duration,
            "answer": data.get("answer"),
            "context_count": len(data.get("context_docs", []))
        }
    else:
        return {
            "status": "error",
            "status_code": response.status_code,
            "duration": duration,
            "text": response.text
        }

def run_trials():
    print("--- Memulai Ujicoba RAG ---")
    
    # Trial 1: General academic query
    print("\nTrial 1: General Query (Akademik)")
    res1 = test_query("Apa saja tugas saya yang akan datang?")
    print(f"Durasi: {res1['duration']:.2f}s | Konteks: {res1['context_count']}")
    
    # Trial 2: Time-sensitive query (with time)
    print("\nTrial 2: Time-Sensitive (With Time Context)")
    res2 = test_query("Apa jadwal saya hari ini?", include_time=True)
    print(f"Durasi: {res2['duration']:.2f}s | Answer: {res2['answer'][:100]}...")
    
    # Trial 3: Time-sensitive query (without time)
    print("\nTrial 3: Time-Sensitive (Without Time Context)")
    res3 = test_query("Apa jadwal saya sekarang?", include_time=False)
    print(f"Durasi: {res3['duration']:.2f}s | Answer: {res3['answer'][:100]}...")

    # Summary report for Methodology
    print("\n--- Summary for Methodology ---")
    avg_speed = (res1['duration'] + res2['duration'] + res3['duration']) / 3
    print(f"Average Response Time: {avg_speed:.2f}s")
    print(f"Time Context Success: {'Yes' if 'hari ini' in res2['answer'].lower() or 'senin' in res2['answer'].lower() else 'No'}")

if __name__ == "__main__":
    run_trials()
