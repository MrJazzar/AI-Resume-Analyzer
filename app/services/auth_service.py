"""
Authentication business logic: registration, login, logout, and
session-based current-user lookup. Kept separate from the route layer
so routes stay thin and this logic is independently testable.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister
from app.utils.exceptions import BadRequestError, UnauthorizedError
from app.utils.security import generate_session_token, hash_password, verify_password


def register_user(db: DBSession, payload: UserRegister) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise BadRequestError("Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: DBSession, payload: UserLogin) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    return user


def create_session(db: DBSession, user: User) -> SessionModel:
    token = generate_session_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
    session = SessionModel(id=token, user_id=user.id, expires_at=expires_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_user_from_session(db: DBSession, session_token: str | None) -> User:
    if not session_token:
        raise UnauthorizedError("Not authenticated")

    session = db.query(SessionModel).filter(SessionModel.id == session_token).first()
    if not session:
        raise UnauthorizedError("Invalid or expired session")

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        raise UnauthorizedError("Session expired")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise UnauthorizedError("User not found")
    return user


def delete_session(db: DBSession, session_token: str | None) -> None:
    if not session_token:
        return
    session = db.query(SessionModel).filter(SessionModel.id == session_token).first()
    if session:
        db.delete(session)
        db.commit()
