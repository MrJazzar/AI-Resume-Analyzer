from datetime import datetime

from pydantic import BaseModel


class JobOut(BaseModel):
    id: int
    title: str
    company: str | None = None
    description: str | None = None
    required_skills: str | None = None
    experience: str | None = None
    location: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
