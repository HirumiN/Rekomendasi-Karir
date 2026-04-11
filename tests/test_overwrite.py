import pytest
import asyncio
from app.models import CareerResult, Roadmap, RoadmapStep, Todo, CareerProgress, User
from app.main import app
from app import auth
from app import db as app_db
from httpx import AsyncClient, ASGITransport
from tests.conftest import override_get_db

# Override dependency globally for the test app
app.dependency_overrides[app_db.get_db] = override_get_db

from unittest.mock import MagicMock
from app import calendar_service
calendar_service.create_todo_event = MagicMock(return_value="mock_event_id")

@pytest.mark.asyncio
async def test_overwrite_career_logic(session):
    # Setup test user
    from app.models import User
    test_user = session.query(User).filter_by(email="test@example.com").first()
    if not test_user:
         from app import crud, schemas
         test_user = crud.create_user(session, schemas.UserCreate(nama="Test User", email="test@example.com"))
    
    # Dynamic Mock Auth
    def mock_get_current_active_user():
        return test_user
    app.dependency_overrides[auth.get_current_active_user] = mock_get_current_active_user
    
    user_id = test_user.id_user

    # Mock Data v1
    data_v1 = {
        "careers": [{"name": "Karir V1", "reason": "Reason v1", "strengths": ["s1"], "weaknesses": ["w1"]}],
        "roadmap": [{"phase": "P1", "steps": [{"title": "Step V1", "description": "desc v1", "skill_tags": ["v1"], "xp_reward": 50}]}],
        "tasks": [{"task": "Task V1", "priority": "Tinggi", "deadline": "2026-05-01"}]
    }

    # Mock Data v2
    data_v2 = {
        "careers": [{"name": "Karir V2", "reason": "Reason v2", "strengths": ["s2"], "weaknesses": ["w2"]}],
        "roadmap": [{"phase": "P2", "steps": [{"title": "Step V2", "description": "desc v2", "skill_tags": ["v2"], "xp_reward": 100}]}],
        "tasks": [{"task": "Task V2", "priority": "Tinggi", "deadline": "2026-06-01"}]
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Save v1
        res1 = await ac.post(f"/api/ai/career-analysis/save?user_id={user_id}", json=data_v1)
        assert res1.status_code == 200

        # Verify v1 exists
        from tests.conftest import TestingSessionLocal
        verify_session = TestingSessionLocal()
        try:
            assert verify_session.query(CareerResult).filter_by(id_user=user_id).count() == 1
            assert verify_session.query(Todo).filter_by(id_user=user_id, nama="Task V1").count() == 1

            # Save v2 (Overwrite)
            res2 = await ac.post(f"/api/ai/career-analysis/save?user_id={user_id}", json=data_v2)
            assert res2.status_code == 200

            # Verify v1 is GONE and v2 exists
            verify_session.expire_all() # Ensure fresh data
            assert verify_session.query(CareerResult).filter_by(id_user=user_id).count() == 1
            assert verify_session.query(CareerResult).filter_by(id_user=user_id).first().career_name == "Karir V2"
            
            # Verify old tasks are GONE
            assert verify_session.query(Todo).filter_by(id_user=user_id, nama="Task V1").count() == 0
            assert verify_session.query(Todo).filter_by(id_user=user_id, nama="Task V2").count() == 1
        finally:
            verify_session.close()

    print("Overwrite test PASSED")
