from pydantic import BaseModel


class RecommendationOut(BaseModel):
    job_id: int
    title: str
    company: str | None = None
    score: int
    matched_skills: list[str]
    missing_skills: list[str]


class RecommendationDetailOut(RecommendationOut):
    explanation: str | None = None
