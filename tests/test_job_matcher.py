import json
import pytest
from app.models.job import Job
from app.models.resume_analysis import ResumeAnalysis
from app.services.job_matcher import match_job_and_resume


def test_matcher_100_percent_match():
    job = Job(required_skills=json.dumps(["Python", "FastAPI", "SQL"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python", "FastAPI", "SQL"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    assert result.matched_skills == ["FastAPI", "Python", "SQL"]
    assert result.missing_skills == []


def test_matcher_0_percent_match():
    job = Job(required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Java", "Spring"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 0
    assert result.matched_skills == []
    assert result.missing_skills == ["FastAPI", "Python"]


def test_matcher_partial_match():
    job = Job(required_skills=json.dumps(["Python", "FastAPI", "Docker", "AWS", "SQL"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python", "FastAPI", "SQL", "Git"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 60
    assert result.matched_skills == ["FastAPI", "Python", "SQL"]
    assert sorted(result.missing_skills) == ["AWS", "Docker"]


def test_matcher_empty_candidate_skills():
    job = Job(required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps([]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 0
    assert result.matched_skills == []
    assert result.missing_skills == ["FastAPI", "Python"]


def test_matcher_empty_required_skills():
    job = Job(required_skills=json.dumps([]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python", "FastAPI"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    assert result.matched_skills == []
    assert result.missing_skills == []


def test_matcher_case_insensitive():
    job = Job(required_skills=json.dumps(["Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["python", "fastapi"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    assert result.matched_skills == ["FastAPI", "Python"]
    assert result.missing_skills == []


def test_matcher_whitespace_differences():
    job = Job(required_skills=json.dumps([" Python ", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["python", "   fastapi   "]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    # Original casing preserved and whitespaces stripped
    assert result.matched_skills == ["FastAPI", "Python"]
    assert result.missing_skills == []



def test_matcher_duplicate_skills():
    job = Job(required_skills=json.dumps(["Python", "Python", "FastAPI"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["python", "fastapi"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    assert len(result.matched_skills) == 2


def test_matcher_extra_candidate_skills():
    job = Job(required_skills=json.dumps(["Python"]))
    analysis = ResumeAnalysis(technical_skills=json.dumps(["Python", "Java", "Docker"]))
    result = match_job_and_resume(job, analysis)
    assert result.score == 100
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == []


def test_matcher_comma_separated_fallback():
    job = Job(required_skills="Python, FastAPI, SQL")
    analysis = ResumeAnalysis(technical_skills="python, fastapi, git")
    result = match_job_and_resume(job, analysis)
    assert result.score == 67  # 2 out of 3 matches (66.6666% rounded is 67)
    assert result.matched_skills == ["FastAPI", "Python"]
    assert result.missing_skills == ["SQL"]
