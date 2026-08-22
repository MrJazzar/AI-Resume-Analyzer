import json
from app.models.job import Job
from tests.conftest import TestingSessionLocal


def register_and_login(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Employer", "email": "employer@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 201
    return response.json()


def test_create_job_unauthenticated(client):
    data = {
        "title": "AI Engineer",
        "company": "DeepMind",
        "required_skills": ["Python"]
    }
    response = client.post("/api/jobs/", json=data)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_create_job_success(client):
    register_and_login(client)

    data = {
        "title": "AI Research Scientist",
        "company": "DeepMind London",
        "description": "Researching next generation LLMs.",
        "required_skills": ["Python", "JAX", "Research"],
        "experience": "5+ years",
        "location": "London"
    }
    response = client.post("/api/jobs/", json=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["id"] is not None
    assert res_data["title"] == "AI Research Scientist"
    assert res_data["company"] == "DeepMind London"
    assert res_data["experience"] == "5+ years"
    assert res_data["location"] == "London"

    # Verify database persistence
    db = TestingSessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == res_data["id"]).first()
        assert db_job is not None
        assert db_job.title == "AI Research Scientist"
        assert db_job.company == "DeepMind London"
        # Since it is stored as JSON string in sqlite
        skills = json.loads(db_job.required_skills)
        assert skills == ["Python", "JAX", "Research"]
    finally:
        db.close()


def test_create_job_missing_required_title(client):
    register_and_login(client)

    # Missing 'title'
    data = {
        "company": "DeepMind",
        "required_skills": ["Python"]
    }
    response = client.post("/api/jobs/", json=data)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_create_job_invalid_type(client):
    register_and_login(client)

    # Title is integer instead of string
    data = {
        "title": 99999,
        "company": "DeepMind"
    }
    response = client.post("/api/jobs/", json=data)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_list_jobs_empty(client):
    response = client.get("/api/jobs/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_jobs_with_data(client):
    register_and_login(client)
    data = {"title": "Fullstack Developer", "company": "GitHub"}
    client.post("/api/jobs/", json=data)

    client.cookies.clear()  # Simulate unauthenticated client

    response = client.get("/api/jobs/")
    assert response.status_code == 200
    res_list = response.json()
    assert len(res_list) >= 1
    assert res_list[0]["title"] == "Fullstack Developer"
    assert res_list[0]["company"] == "GitHub"


def test_get_job_by_id_exists(client):
    register_and_login(client)
    data = {"title": "DevOps Engineer", "company": "HashiCorp"}
    post_resp = client.post("/api/jobs/", json=data)
    job_id = post_resp.json()["id"]

    client.cookies.clear()  # Simulate unauthenticated client

    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["title"] == "DevOps Engineer"
    assert res_data["company"] == "HashiCorp"


def test_get_job_by_id_not_found(client):
    response = client.get("/api/jobs/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_update_job_success(client):
    register_and_login(client)
    create_resp = client.post("/api/jobs/", json={"title": "Data Scientist", "company": "Meta"})
    job_id = create_resp.json()["id"]

    update_data = {
        "title": "Lead Data Scientist",
        "required_skills": ["Python", "PyTorch", "Statistics"]
    }
    update_resp = client.put(f"/api/jobs/{job_id}", json=update_data)
    assert update_resp.status_code == 200
    res_data = update_resp.json()
    assert res_data["title"] == "Lead Data Scientist"
    assert res_data["company"] == "Meta"

    db = TestingSessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == job_id).first()
        assert db_job.title == "Lead Data Scientist"
        assert json.loads(db_job.required_skills) == ["Python", "PyTorch", "Statistics"]
    finally:
        db.close()


def test_update_job_not_found(client):
    register_and_login(client)
    response = client.put("/api/jobs/99999", json={"title": "New Title"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_update_job_invalid_data(client):
    register_and_login(client)
    create_resp = client.post("/api/jobs/", json={"title": "Data Scientist", "company": "Meta"})
    job_id = create_resp.json()["id"]

    response = client.put(f"/api/jobs/{job_id}", json={"title": ""})
    assert response.status_code == 400


def test_update_job_unauthenticated(client):
    db = TestingSessionLocal()
    job = Job(title="Unprotected Job")
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    response = client.put(f"/api/jobs/{job_id}", json={"title": "New Title"})
    assert response.status_code == 401


