def test_career_root(client):
    response = client.get("/api/career/")
    assert response.status_code in [200, 401]


def test_missing_skills_requires_auth(client):
    response = client.get(
        "/api/career/missing-skills/1?target_career=AI%20Engineer"
    )
    assert response.status_code in [401, 404]


def test_roadmap_requires_auth(client):
    response = client.get(
        "/api/career/roadmap/1?target_career=AI%20Engineer"
    )
    assert response.status_code in [401, 404]


def test_advice_requires_auth(client):
    response = client.get(
        "/api/career/advice/1?target_career=AI%20Engineer"
    )
    assert response.status_code in [401, 404]


def test_career_ask_requires_auth(client):
    response = client.post(
        "/api/career/ask",
        json={
            "question": "What should I learn to become an AI Engineer?",
            "target_career": "AI Engineer",
        },
    )
    assert response.status_code in [401, 404]