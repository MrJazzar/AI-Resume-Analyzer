from datetime import datetime
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    required_skills: list[str] | None = Field(default=None)
    experience: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)

    model_config = {
        "extra": "forbid"
    }


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    required_skills: list[str] | None = Field(default=None)
    experience: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)

    model_config = {
        "extra": "forbid"
    }


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

