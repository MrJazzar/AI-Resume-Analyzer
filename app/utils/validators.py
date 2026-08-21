"""Shared validation helpers for uploaded resume documents."""

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def has_allowed_extension(filename: str, allowed: set[str] = ALLOWED_RESUME_EXTENSIONS) -> bool:
    """Case-insensitive extension check, e.g. has_allowed_extension('cv.PDF') -> True."""
    return any(filename.lower().endswith(ext) for ext in allowed)


def is_within_size_limit(size_bytes: int, max_bytes: int = MAX_RESUME_SIZE_BYTES) -> bool:
    return 0 < size_bytes <= max_bytes


