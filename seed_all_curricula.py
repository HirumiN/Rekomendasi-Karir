import os
import sys
from app import db
from import_csv import import_from_csv

def seed_all():
    base_dir = "/home/hirumi/Documents/TAAI/fastapi-simple-rag/kurikulum"
    
    print(f"Starting bulk seeding from {base_dir}...")
    
    csv_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Sort files to ensure consistent import order (e.g. PENS.csv first if it exists)
    csv_files.sort()
    
    for i, file_path in enumerate(csv_files):
        print(f"\n[{i+1}/{len(csv_files)}] Importing: {file_path}")
        try:
            import_from_csv(file_path)
        except Exception as e:
            print(f"Error importing {file_path}: {e}")

if __name__ == "__main__":
    # Ensure app is in python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    seed_all()
