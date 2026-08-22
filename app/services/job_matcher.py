import json
from pydantic import BaseModel
from app.models.job import Job
from app.models.resume_analysis import ResumeAnalysis


class JobMatchResult(BaseModel):
    score: int
    matched_skills: list[str]
    missing_skills: list[str]


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


def match_job_and_resume(job: Job, analysis: ResumeAnalysis | None) -> JobMatchResult:
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
        return JobMatchResult(
            score=100,
            matched_skills=[],
            missing_skills=[]
        )

    # Compute matches and missing sets
    matched_set = required_set.intersection(candidate_set)
    missing_set = required_set.difference(candidate_set)

    # Calculate score
    score = round((len(matched_set) / len(required_set)) * 100)

    # Restore original casing from display map
    matched_skills = [display_map[s] for s in sorted(matched_set)]
    missing_skills = [display_map[s] for s in sorted(missing_set)]

    return JobMatchResult(
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills
    )
