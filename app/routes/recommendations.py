"""
Job recommendation endpoints (Job Matching Agent output). Scaffolded by
Member 1; implemented by Member 3.

Expected endpoints per spec:
  GET /api/recommendations/{resume_id}
  GET /api/recommendations/{resume_id}/{job_id}
"""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/{resume_id}")
def get_recommendations(resume_id: int, current_user: User = Depends(get_current_user)):
    """TODO(Member 3): return ranked job matches for this resume."""
    return {"detail": "Not implemented yet"}


@router.get("/{resume_id}/{job_id}")
def get_recommendation_detail(
    resume_id: int, job_id: int, current_user: User = Depends(get_current_user)
):
    """TODO(Member 3): return match score + explanation for one job."""
    return {"detail": "Not implemented yet"}
