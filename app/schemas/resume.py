from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetail(ResumeOut):
    raw_text: str | None = None


class ResumeAnalysisOut(BaseModel):
    id: int
    resume_id: int
    summary: str | None = None
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
