import json
import httpx
from pydantic import BaseModel
from app.config import settings
from app.models.job import Job
from app.models.resume_analysis import ResumeAnalysis


class JobMatchResult(BaseModel):
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str | None = None


def parse_skills_field(field_value: str | None) -> list[str]:
    """
    Parses a skills field which could be stored as a JSON string list
    or a comma-separated plain text string.
    """
    if not field_value or not field_value.strip():
        return []

    stripped_val = field_value.strip()

    # Try parsing as JSON list
    if (stripped_val.startswith("[") and stripped_val.endswith("]")) or (
        stripped_val.startswith("{") and stripped_val.endswith("}")
    ):
        try:
            parsed = json.loads(stripped_val)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback to comma-separated string
    return [s.strip() for s in stripped_val.split(",") if s.strip()]


def generate_match_explanation(
    score: int,
    matched_skills: list[str],
    missing_skills: list[str],
    job_title: str,
    company: str | None = None,
) -> str:
    """
    Generates a human-readable match explanation using the Gemini API,
    grounded strictly in the deterministic matching results.
    """
    fallback_text = (
        f"The candidate is a {score}% match for the {job_title} role at {company or 'the company'}. "
        f"Matched skills: {', '.join(matched_skills) if matched_skills else 'None'}. "
        f"Missing skills: {', '.join(missing_skills) if missing_skills else 'None'}."
    )

    if not settings.AI_API_KEY:
        return fallback_text

    prompt = (
        "You are an AI career assistant. Write a short, professional, 1-2 sentence explanation of "
        "how well the candidate matches the job based ONLY on these facts. "
        "Do NOT invent skills, do NOT change the match score, and do NOT add external assumptions.\n\n"
        f"Job Title: {job_title}\n"
        f"Company: {company or 'the company'}\n"
        f"Match Score: {score}%\n"
        f"Matched Skills: {matched_skills}\n"
        f"Missing Skills: {missing_skills}\n"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent"
    try:
        response = httpx.post(
            url,
            params={"key": settings.AI_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                },
            },
            timeout=10,
        )
        response.raise_for_status()
        result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return result_text.strip()
    except Exception:
        return fallback_text


def match_job_and_resume(
    job: Job,
    analysis: ResumeAnalysis | None,
    generate_explanation: bool = False,
) -> JobMatchResult:
    """
    Compares the Job required skills with the ResumeAnalysis technical skills
    and returns a deterministic match score and skill lists.
    """
    required_skills_raw = parse_skills_field(job.required_skills)
    candidate_skills_raw = parse_skills_field(analysis.technical_skills if analysis else None)

    # Normalize candidate skills (lowercase & stripped)
    candidate_set = {s.lower().strip() for s in candidate_skills_raw if s.strip()}

    # Normalize required skills, keeping a map back to original display casing
    required_set = set()
    display_map = {}
    for skill in required_skills_raw:
        norm = skill.lower().strip()
        if norm:
            required_set.add(norm)
            # Retain the first casing encountered for display
            if norm not in display_map:
                display_map[norm] = skill

    # Edge case: Job has no required skills
    if not required_set:
        explanation = None
        if generate_explanation:
            explanation = f"The candidate is a 100% match for the {job.title} role at {job.company or 'the company'}."
        return JobMatchResult(
            score=100,
            matched_skills=[],
            missing_skills=[],
            explanation=explanation,
        )

    # Compute matches and missing sets
    matched_set = required_set.intersection(candidate_set)
    missing_set = required_set.difference(candidate_set)

    # Calculate score
    score = round((len(matched_set) / len(required_set)) * 100)

    # Restore original casing from display map
    matched_skills = [display_map[s] for s in sorted(matched_set)]
    missing_skills = [display_map[s] for s in sorted(missing_set)]

    explanation = None
    if generate_explanation:
        explanation = generate_match_explanation(
            score=score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            job_title=job.title,
            company=job.company,
        )

    return JobMatchResult(
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        explanation=explanation,
    )

