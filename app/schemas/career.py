from pydantic import BaseModel


class CareerAskRequest(BaseModel):
    question: str
    resume_id: int | None = None
    target_career: str | None = None


class CareerAdviceResponse(BaseModel):
    career: str
    missing_skills: list[str]
    learning_path: list[str]
    projects: list[str]
    certifications: list[str]
    resume_improvements: list[str]