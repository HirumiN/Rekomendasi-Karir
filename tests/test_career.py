import pytest
from app.models import CareerResult, Roadmap, RoadmapStep, Todo, CareerProgress, User
from app.main import app
from app import auth

def mock_get_current_active_user():
    return User(
        id_user=1,
        nama="Test User",
        email="test@example.com"
    )

app.dependency_overrides[auth.get_current_active_user] = mock_get_current_active_user

def test_generate_and_save_career(client, session):
    # conftest.py creates a test user. Let's retrieve it to get the correct user_id.
    from app.models import User
    test_user = session.query(User).first()
    assert test_user is not None
    user_id = test_user.id_user

    # 1. Test Generate
    # This calls Gemini, so it requires internet and API keys to be valid.
    # If API keys are from .env and valid, it will fetch a real response.
    response_gen = client.post(f"/api/ai/career-analysis/generate?user_id={user_id}")
    assert response_gen.status_code == 200, response_gen.text
    response_json = response_gen.json()
    assert "data" in response_json
    data = response_json["data"]
    assert "career" in data
    
    # 2. Test Save
    response_save = client.post(f"/api/ai/career-analysis/save?user_id={user_id}", json=data)
    assert response_save.status_code == 200, response_save.text
    
    # 3. Verify Database Entries
    # Create a fresh database connection to avoid pytest session isolation caching
    from tests.conftest import TestingSessionLocal
    fresh_session = TestingSessionLocal()
    
    saved_career = fresh_session.query(CareerResult).filter_by(id_user=user_id).first()
    assert saved_career is not None, "Career result not saved to DB"
    assert saved_career.career_name == data["career"]["name"]

    saved_roadmap = fresh_session.query(Roadmap).filter_by(id_user=user_id).first()
    assert saved_roadmap is not None, "Roadmap not saved to DB"
    
    saved_steps = fresh_session.query(RoadmapStep).filter_by(id_roadmap=saved_roadmap.id).all()
    assert len(saved_steps) > 0, "Roadmap steps not saved to DB"

    saved_progress = fresh_session.query(CareerProgress).filter_by(id_user=user_id).all()
    assert len(saved_progress) > 0, "Career progress not saved to DB"
    assert len(saved_progress) == len(saved_steps)

    saved_todos = fresh_session.query(Todo).filter_by(id_user=user_id).all()
    if "tasks" in data and len(data["tasks"]) > 0:
        assert len(saved_todos) > 0, "Todos not saved to DB"
        
    fresh_session.close()
