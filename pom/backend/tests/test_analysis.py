import pytest
from models import User, AnalysisHistory
from auth import get_password_hash
import json

@pytest.fixture
def analysis_user(db_session):
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        email="analysis@example.com",
        username="analysisuser",
        hashed_password=hashed,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def analysis_token(client, analysis_user):
    response = client.post("/api/users/login", json={
        "username": "analysisuser",
        "password": "password123"
    })
    return response.json()["access_token"]

@pytest.fixture
def seed_analysis_history(db_session, analysis_user):
    # Add a few history records
    h1 = AnalysisHistory(
        user_id=analysis_user.id,
        exercise_name="biceps",
        video_filename="biceps1.mp4",
        feedback="Good job",
        avg_rating=85.5,
        joint_ratings={"elbow": 90, "shoulder": 80}
    )
    h2 = AnalysisHistory(
        user_id=analysis_user.id,
        exercise_name="squats",
        video_filename="squats1.mp4",
        feedback="Keep back straight",
        avg_rating=70.0,
        joint_ratings={"knee": 60, "hip": 80}
    )
    db_session.add(h1)
    db_session.add(h2)
    db_session.commit()
    return [h1, h2]

def test_get_analysis_history_all(client, analysis_token, seed_analysis_history):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    response = client.get("/api/analysis/history", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["analyses"]) == 2
    # Check ordering (most recent first) - though created at same time might be tricky, 
    # usually insertion order or slight timestamp diff handles it.
    # Let's just check content.
    names = [a["exercise_name"] for a in data["analyses"]]
    assert "biceps" in names
    assert "squats" in names

def test_get_analysis_history_filter(client, analysis_token, seed_analysis_history):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    response = client.get("/api/analysis/history?exercise_name=biceps", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["analyses"][0]["exercise_name"] == "biceps"

def test_get_analysis_history_pagination(client, analysis_token, seed_analysis_history):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    # Limit 1
    response = client.get("/api/analysis/history?limit=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["analyses"]) == 1
    assert data["total"] == 2 # Total count should still be 2

def test_get_analysis_by_id_success(client, analysis_token, seed_analysis_history):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    target_id = seed_analysis_history[0].id
    
    response = client.get(f"/api/analysis/history/{target_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_id
    assert data["exercise_name"] == seed_analysis_history[0].exercise_name

def test_get_analysis_by_id_not_found(client, analysis_token):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    response = client.get("/api/analysis/history/99999", headers=headers)
    assert response.status_code == 404

def test_delete_analysis_success(client, db_session, analysis_token, seed_analysis_history):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    target_id = seed_analysis_history[0].id
    
    response = client.delete(f"/api/analysis/history/{target_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify deletion
    deleted = db_session.query(AnalysisHistory).filter(AnalysisHistory.id == target_id).first()
    assert deleted is None

def test_delete_analysis_not_found(client, analysis_token):
    headers = {"Authorization": f"Bearer {analysis_token}"}
    response = client.delete("/api/analysis/history/99999", headers=headers)
    assert response.status_code == 404
