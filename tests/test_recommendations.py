import json
import httpx
import pytest
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.job import Job
from tests.conftest import TestingSessionLocal


def register_and_login(client, email="employer@example.com"):
    response = client.post(
        "/api/auth/register",
        json={"name": "Employer", "email": email, "password": "SecurePass123"},
    )
    assert response.status_code == 201
    return response.json()


def create_mock_analysis(user_id):
    db = TestingSessionLocal()
    try:
        # Create Resume
        resume = Resume(
            user_id=user_id,
            filename="cv.pdf",
            file_path="uploads/cv.pdf",
            raw_text="Python Developer, FastAPI, SQL"
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # Create Analysis
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            summary="Python coder",
            technical_skills=json.dumps(["Python", "FastAPI", "SQL"]),
            soft_skills=json.dumps([]),
            education=json.dumps([]),
            experience=json.dumps([]),
            projects=json.dumps([])
        )
        db.add(analysis)
        db.commit()
        return resume.id
    finally:
        db.close()


def test_recommendations_unauthenticated(client):
    response = client.get("/api/recommendations/1")
    assert response.status_code == 401


def test_recommendations_user_without_analysis(client):
    register_and_login(client, email="noanalysis@example.com")
    # Query non-existent resume ID
    response = client.get("/api/recommendations/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_recommendations_empty_jobs(client):
    user = register_and_login(client, email="emptyjobs@example.com")
    resume_id = create_mock_analysis(user["id"])

    response = client.get(f"/api/recommendations/{resume_id}")
    assert response.status_code == 200
    assert response.json() == []


def test_recommendations_sorting_and_matching(client, monkeypatch):
    user = register_and_login(client, email="success@example.com")
    resume_id = create_mock_analysis(user["id"])

    # Populate jobs
    db = TestingSessionLocal()
    try:
        # Job 1: 100% Match
        j1 = Job(title="Python Expert", company="Google", required_skills=json.dumps(["Python", "FastAPI"]))
        # Job 2: 50% Match
        j2 = Job(title="Backend Dev", company="Meta", required_skills=json.dumps(["Python", "Java"]))
        # Job 3: 0% Match
        j3 = Job(title="Frontend Dev", company="Netflix", required_skills=json.dumps(["React", "CSS"]))
        db.add_all([j1, j2, j3])
        db.commit()
        j1_id, j2_id, j3_id = j1.id, j2.id, j3.id
    finally:
        db.close()

    # Query recommendations
    response = client.get(f"/api/recommendations/{resume_id}")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) == 3

    # Assert descending sort by score
    assert recs[0]["score"] == 100
    assert recs[0]["job_id"] == j1_id
    assert recs[0]["matched_skills"] == ["FastAPI", "Python"]
    assert recs[0]["missing_skills"] == []

    assert recs[1]["score"] == 50
    assert recs[1]["job_id"] == j2_id
    assert recs[1]["matched_skills"] == ["Python"]
    assert recs[1]["missing_skills"] == ["Java"]

    assert recs[2]["score"] == 0
    assert recs[2]["job_id"] == j3_id
    assert recs[2]["matched_skills"] == []
    assert recs[2]["missing_skills"] == ["CSS", "React"]


def test_recommendation_detail_unauthenticated(client):
    response = client.get("/api/recommendations/1/1")
    assert response.status_code == 401


def test_recommendation_detail_success(client, monkeypatch):
    user = register_and_login(client, email="detail@example.com")
    resume_id = create_mock_analysis(user["id"])

    # Populate job
    db = TestingSessionLocal()
    try:
        job = Job(title="Backend Python Developer", company="GitHub", required_skills=json.dumps(["Python", "FastAPI", "Docker"]))
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    from app.config import settings
    monkeypatch.setattr(settings, "AI_API_KEY", "mock-key")

    # Mock Gemini post response
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: type("MockResponse", (), {
            "status_code": 200,
            "raise_for_status": lambda self: None,
            "json": lambda self: {
                "candidates": [{"content": {"parts": [{"text": "Candidate matches backend skills well."}]}}]
            }
        })()
    )

    response = client.get(f"/api/recommendations/{resume_id}/{job_id}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["job_id"] == job_id
    assert res_data["title"] == "Backend Python Developer"
    assert res_data["company"] == "GitHub"
    assert res_data["score"] == 67  # 2 matching skills out of 3 (66.666% rounded is 67)
    assert res_data["matched_skills"] == ["FastAPI", "Python"]
    assert res_data["missing_skills"] == ["Docker"]
    assert res_data["explanation"] == "Candidate matches backend skills well."
