from unittest.mock import Mock, patch

from app.services.career_advisor import CareerAdvisor


def test_get_resume_skills():
    advisor = CareerAdvisor.__new__(CareerAdvisor)

    analysis = Mock()
    analysis.technical_skills = "Python, Machine Learning, FastAPI"

    skills = advisor.get_resume_skills(analysis)

    assert skills == [
        "Python",
        "Machine Learning",
        "FastAPI",
    ]