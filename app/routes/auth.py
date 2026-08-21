from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import MessageResponse, UserLogin, UserOut, UserRegister
from app.services import auth_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, payload)
    session = auth_service.create_session(db, user)
    _set_session_cookie(response, session.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload)
    session = auth_service.create_session(db, user)
    _set_session_cookie(response, session.id)
    return user


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
):
    auth_service.delete_session(db, session_id)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
