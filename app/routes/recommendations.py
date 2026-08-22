"""
Job recommendation endpoints (Job Matching Agent output). Implemented by Member 3.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.services.job_matcher import match_job_and_resume
from app.schemas.recommendation import RecommendationOut, RecommendationDetailOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _get_user_resume(db: Session, resume_id: int, current_user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.analysis is None:
        raise HTTPException(status_code=404, detail="Resume analysis not found")
    return resume


@router.get("/{resume_id}", response_model=list[RecommendationOut])
def get_recommendations(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_user_resume(db, resume_id, current_user)
    jobs = db.query(Job).all()

    recommendations = []
    for job in jobs:
        match_result = match_job_and_resume(job, resume.analysis, generate_explanation=False)
        recommendations.append(
            RecommendationOut(
                job_id=job.id,
                title=job.title,
                company=job.company,
                score=match_result.score,
                matched_skills=match_result.matched_skills,
                missing_skills=match_result.missing_skills,
            )
        )

    # Sort DESC by score
    recommendations.sort(key=lambda r: r.score, reverse=True)
    return recommendations


@router.get("/{resume_id}/{job_id}", response_model=RecommendationDetailOut)
def get_recommendation_detail(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_user_resume(db, resume_id, current_user)
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    match_result = match_job_and_resume(job, resume.analysis, generate_explanation=True)
    return RecommendationDetailOut(
        job_id=job.id,
        title=job.title,
        company=job.company,
        score=match_result.score,
        matched_skills=match_result.matched_skills,
        missing_skills=match_result.missing_skills,
        explanation=match_result.explanation,
    )

