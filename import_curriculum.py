import csv
import httpx
import sys
import os

# Configuration
API_URL = "http://localhost:8000/api/import-kurikulum"
# You might need to provide an auth token if the endpoint is protected
# AUTH_TOKEN = "your_token_here"

def import_csv(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    print(f"Sending {len(data)} rows to {API_URL}...")
    
    try:
        # Note: If auth is required, add headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = httpx.post(API_URL, json=data, timeout=60.0)
        response.raise_for_status()
        print("Success!")
        print(response.json())
    except Exception as e:
        print(f"Failed to import: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_curriculum.py path/to/your/file.csv")
    else:
        import_csv(sys.argv[1])
