"""
Job listing endpoints. Scaffolded by Member 1; implemented by later
members.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobOut, JobUpdate
from app.schemas.user import MessageResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = Job(
        title=payload.title,
        company=payload.company,
        description=payload.description,
        required_skills=json.dumps(payload.required_skills) if payload.required_skills is not None else None,
        experience=payload.experience,
        location=payload.location,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@router.get("/search", response_model=list[JobOut])
def search_jobs(skill: str | None = None, db: Session = Depends(get_db)):
    if not skill or not skill.strip():
        raise HTTPException(status_code=400, detail="Skill query parameter is required")

    all_jobs = db.query(Job).all()
    results = []
    for job in all_jobs:
        if not job.required_skills:
            continue
        try:
            skills = json.loads(job.required_skills)
            if isinstance(skills, list):
                if any(skill.lower() == s.lower() for s in skills):
                    results.append(job)
                continue
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback to comma-separated check
        skills = [s.strip().lower() for s in job.required_skills.split(",")]
        if skill.lower() in skills:
            results.append(job)

    return results


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    payload: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "required_skills":
            setattr(job, key, json.dumps(value) if value is not None else None)
        else:
            setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", response_model=MessageResponse)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"detail": "Job deleted successfully"}




