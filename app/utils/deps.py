"""
Reusable FastAPI dependencies. Other route modules (resumes.py, jobs.py,
career.py) should import `get_current_user` to protect endpoints, e.g.:

    from app.utils.deps import get_current_user

    @router.get("/mine")
    def my_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        ...
"""

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_user_from_session


def get_current_user(
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
) -> User:
    return get_user_from_session(db, session_id)
