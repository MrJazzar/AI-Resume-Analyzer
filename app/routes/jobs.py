"""
Job listing endpoints. Scaffolded by Member 1; implemented by later
members.
"""

from fastapi import APIRouter, Depends

from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    """TODO: return job postings."""
    return {"detail": "Not implemented yet"}
