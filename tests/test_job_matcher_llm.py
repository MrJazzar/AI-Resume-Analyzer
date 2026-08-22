import json
import httpx
import pytest
from app.models.job import Job
from app.models.resume_analysis import ResumeAnalysis
from app.services.job_matcher import match_job_and_resume, generate_match_explanation
from app.config import settings


def test_explanation_success(monkeypatch):
    # Mock settings to ensure key exists
    monkeypatch.setattr(settings, "AI_API_KEY", "mock-key")

    # Mock httpx.post to return a successful mocked Gemini response
    def mock_post(url, *args, **kwargs):
        class MockResponse:
            status_code = 200
            def raise_for_status(self):
                pass
            def json(self):
                return {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": "The candidate has strong Python and FastAPI skills."
                                    }
                                ]
                            }
                        }
                    ]
                }
        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    job = Job(title="Python Developer", company="Google", required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python", "FastAPI"]))

    result = match_job_and_resume(job, analysis, generate_explanation=True)
    assert result.score == 100
    assert result.matched_skills == ["FastAPI", "Python"]
    assert result.missing_skills == []
    assert result.explanation == "The candidate has strong Python and FastAPI skills."


def test_explanation_graceful_fallback_on_gemini_failure(monkeypatch):
    monkeypatch.setattr(settings, "AI_API_KEY", "mock-key")

    # Mock httpx.post to raise an error
    def mock_post_fail(*args, **kwargs):
        raise httpx.RequestError("Network connection failed")

    monkeypatch.setattr(httpx, "post", mock_post_fail)

    job = Job(title="Python Developer", company="Google", required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python"]))

    result = match_job_and_resume(job, analysis, generate_explanation=True)
    assert result.score == 50
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["FastAPI"]
    assert "The candidate is a 50% match" in result.explanation
    assert "Matched skills: Python" in result.explanation
    assert "Missing skills: FastAPI" in result.explanation


def test_explanation_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "AI_API_KEY", "")

    job = Job(title="Python Developer", company="Google", required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python"]))

    result = match_job_and_resume(job, analysis, generate_explanation=True)
    assert result.score == 50
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["FastAPI"]
    assert "The candidate is a 50% match" in result.explanation
