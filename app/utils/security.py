"""
Security helpers: password hashing/verification and session token generation.
"""

import hashlib
import secrets


def hash_password(plain_password: str) -> str:
    salt = secrets.token_bytes(16)
    # Use PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommendation)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        600000
    )
    # format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    return f"pbkdf2_sha256$600000${salt.hex()}${hash_bytes.hex()}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        original_hash = bytes.fromhex(parts[3])

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations
        )
        return secrets.compare_digest(original_hash, new_hash)
    except Exception:
        return False


def generate_session_token() -> str:
    """Cryptographically secure, URL-safe session token."""
    return secrets.token_urlsafe(48)

