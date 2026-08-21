"""
Database engine and session management (SQLAlchemy + SQLite).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on app startup."""
    # Import models here so they're registered on Base before create_all runs.
    from app.models import job, resume, resume_analysis, session, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
