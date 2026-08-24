from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.career import CareerAskRequest
from app.services.career_advisor import CareerAdvisor
from app.utils.deps import get_current_user


router = APIRouter(
    prefix="/api/career",
    tags=["career"],
)


@router.get("/")
def career_root(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": "Career Advisor API is working"
    }


@router.get("/missing-skills/{resume_id}")
def missing_skills(
    resume_id: int,
    target_career: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id)
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found",
        )

    advisor = CareerAdvisor()

    current_skills = advisor.get_resume_skills(analysis)

    return advisor.find_missing_skills(
        current_skills=current_skills,
        target_career=target_career,
    )


@router.get("/roadmap/{resume_id}")
def career_roadmap(
    resume_id: int,
    target_career: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id)
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found",
        )

    advisor = CareerAdvisor()

    current_skills = advisor.get_resume_skills(analysis)

    return advisor.get_learning_path(
        current_skills=current_skills,
        target_career=target_career,
    )


@router.get("/advice/{resume_id}")
def career_advice(
    resume_id: int,
    target_career: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id)
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found",
        )

    advisor = CareerAdvisor()

    current_skills = advisor.get_resume_skills(analysis)

    return advisor.get_career_advice(
        current_skills=current_skills,
        target_career=target_career,
    )


@router.post("/ask")
def career_ask(
    request: CareerAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    advisor = CareerAdvisor()

    if request.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id == request.resume_id,
                Resume.user_id == current_user.id,
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found",
            )

        analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == request.resume_id
            )
            .first()
        )

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Resume analysis not found",
            )

        current_skills = advisor.get_resume_skills(analysis)

        question = f"""
        User question:
        {request.question}

        Target career:
        {request.target_career or "Not specified"}

        Current resume skills:
        {", ".join(current_skills)}
        """

    else:
        question = request.question

    return advisor.rag.ask(question)