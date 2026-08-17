"""
Generic file-validation helpers for uploaded documents. Scaffolded by
Member 1 as shared infrastructure; Member 2 will use/extend these when
implementing POST /api/resumes/upload (PDF/DOCX validation, size limits,
empty/corrupted file checks).
"""

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def has_allowed_extension(filename: str, allowed: set[str] = ALLOWED_RESUME_EXTENSIONS) -> bool:
    """Case-insensitive extension check, e.g. has_allowed_extension('cv.PDF') -> True."""
    return any(filename.lower().endswith(ext) for ext in allowed)


def is_within_size_limit(size_bytes: int, max_bytes: int = MAX_RESUME_SIZE_BYTES) -> bool:
    return 0 < size_bytes <= max_bytes


# TODO(Member 2): add corrupted-file detection (e.g. attempt to open with
# PyMuPDF / python-docx and catch parse errors) once extraction is implemented.
