import requests

url = "http://127.0.0.1:8000/roadmap/1/adapt/preview" # Assuming roadmap_id 1
headers = {"Authorization": "Bearer dummy"} # Wait, auth is required. The endpoint uses Depends(auth.get_current_active_user).
