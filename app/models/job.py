from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)  # comma-separated or JSON string
    experience = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
