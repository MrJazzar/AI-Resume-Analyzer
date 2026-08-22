import pytest
from pydantic import ValidationError

from app.schemas.job import JobCreate, JobUpdate


def test_valid_job_create():
    data = {
        "title": "AI Engineer",
        "company": "Google DeepMind",
        "description": "Building next-gen AI models.",
        "required_skills": ["Python", "PyTorch", "LLMs"],
        "experience": "3+ years",
        "location": "London"
    }
    schema = JobCreate(**data)
    assert schema.title == "AI Engineer"
    assert schema.company == "Google DeepMind"
    assert schema.description == "Building next-gen AI models."
    assert schema.required_skills == ["Python", "PyTorch", "LLMs"]
    assert schema.experience == "3+ years"
    assert schema.location == "London"


def test_job_create_missing_required_fields():
    data = {
        "company": "DeepMind",
        "location": "London"
    }
    with pytest.raises(ValidationError) as exc:
        JobCreate(**data)
    assert "title" in str(exc.value)


def test_job_create_invalid_types():
    # Title is not a string
    with pytest.raises(ValidationError):
        JobCreate(title=12345)

    # required_skills is not a list
    with pytest.raises(ValidationError):
        JobCreate(title="Software Engineer", required_skills="Python")


def test_valid_job_update():
    data = {
        "title": "Senior AI Engineer",
        "company": "DeepMind"
    }
    schema = JobUpdate(**data)
    assert schema.title == "Senior AI Engineer"
    assert schema.company == "DeepMind"
    assert schema.description is None


def test_partial_job_update():
    schema = JobUpdate(location="New York")
    assert schema.location == "New York"
    assert schema.title is None
    assert schema.company is None


def test_invalid_job_update():
    # Title too short (empty string)
    with pytest.raises(ValidationError):
        JobUpdate(title="")


def test_unsupported_fields_rejected():
    # JobCreate should reject extra fields
    with pytest.raises(ValidationError) as exc:
        JobCreate(title="Engineer", user_id=1)
    assert "user_id" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        JobCreate(title="Engineer", owner_id=2)
    assert "owner_id" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        JobCreate(title="Engineer", is_admin=True)
    assert "is_admin" in str(exc.value)

    # JobUpdate should also reject extra fields
    with pytest.raises(ValidationError) as exc:
        JobUpdate(title="Engineer", user_id=1)
    assert "user_id" in str(exc.value)
