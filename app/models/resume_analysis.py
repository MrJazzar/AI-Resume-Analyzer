from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=True)
    technical_skills = Column(Text, nullable=True)  # JSON string / comma-separated
    soft_skills = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="analysis")
