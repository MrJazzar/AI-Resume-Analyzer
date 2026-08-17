"""
Security helpers: password hashing/verification and session token generation.
"""

import secrets

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def generate_session_token() -> str:
    """Cryptographically secure, URL-safe session token."""
    return secrets.token_urlsafe(48)
