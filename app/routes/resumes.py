"""Resume upload, extraction, analysis, and retrieval endpoints."""

import json
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.schemas.resume import ResumeAnalysisOut, ResumeDetail, ResumeOut
from app.agents.resume_analyzer import analyze_resume
from app.services.resume_extractor import ResumeExtractionError, extract_resume_text
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _get_resume(db: Session, resume_id: int, current_user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


def _analysis_response(analysis: ResumeAnalysis) -> ResumeAnalysisOut:
    values = {field: json.loads(getattr(analysis, field) or "[]") for field in (
        "technical_skills", "soft_skills", "education", "experience", "projects"
    )}
    return ResumeAnalysisOut(
        id=analysis.id, resume_id=analysis.resume_id, summary=analysis.summary,
        created_at=analysis.created_at, **values
    )


@router.post("/upload", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size must not exceed 10 MB")
    if (extension == ".pdf" and not content.startswith(b"%PDF")) or (
        extension == ".docx" and not content.startswith(b"PK")
    ):
        raise HTTPException(status_code=400, detail="The uploaded file is corrupted or has an invalid type")
    try:
        raw_text = extract_resume_text(file.filename or "resume", content)
    except ResumeExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"{uuid.uuid4().hex}{extension}"
    stored_path.write_bytes(content)
    resume = Resume(user_id=current_user.id, filename=file.filename or stored_path.name,
                    file_path=str(stored_path), raw_text=raw_text)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_resume(db, resume_id, current_user)


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisOut)
def analyze_resume_endpoint(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = _get_resume(db, resume_id, current_user)
    if not resume.raw_text:
        raise HTTPException(status_code=400, detail="Resume has no extractable text")
    try:
        result = analyze_resume(resume.raw_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="AI service quota exceeded. Wait and retry, or configure a different API key/model.",
            ) from exc
        raise HTTPException(status_code=502, detail="AI analysis service returned an error") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI analysis service is unavailable") from exc
    analysis = ResumeAnalysis(resume_id=resume.id, summary=result["summary"], **{
        key: json.dumps(result[key]) for key in ("technical_skills", "soft_skills", "education", "experience", "projects")
    })
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return _analysis_response(analysis)


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisOut)
def get_resume_analysis(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = _get_resume(db, resume_id, current_user)
    if resume.analysis is None:
        raise HTTPException(status_code=404, detail="Resume analysis not found")
    return _analysis_response(resume.analysis)
