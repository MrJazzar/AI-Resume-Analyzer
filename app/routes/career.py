"""
Career-advice / analysis endpoints. Scaffolded by Member 1; implemented
by later members (likely the AI/analysis owner).
"""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/career", tags=["career"])


@router.get("/")
def career_root(current_user: User = Depends(get_current_user)):
    """TODO: implement career analysis endpoints."""
    return {"detail": "Not implemented yet"}
