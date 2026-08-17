"""
Resume upload/management endpoints. Scaffolded by Member 1; implemented
by Member 2. Use `Depends(get_current_user)` to protect endpoints and
`Depends(get_db)` for database access — see app/routes/auth.py for an
example.
"""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.get("/")
def list_resumes(current_user: User = Depends(get_current_user)):
    """TODO(Member 2): return the current user's resumes."""
    return {"detail": "Not implemented yet"}
