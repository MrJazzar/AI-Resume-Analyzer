import json
import re

import httpx

from app.config import settings


ANALYSIS_SCHEMA = {
    "summary": "short professional summary",
    "technical_skills": ["skill"],
    "soft_skills": ["skill"],
    "education": [{"university": "", "degree": "", "major": "", "graduation_year": ""}],
    "experience": [{"company": "", "position": "", "duration": "", "responsibilities": []}],
    "projects": [{"name": "", "description": "", "technologies": []}],
}


def analyze_resume(text: str) -> dict:
    """Analyze extracted resume text with the configured Gemini model."""
    if not settings.AI_API_KEY:
        raise RuntimeError("AI_API_KEY is not configured")

    prompt = (
        "You are a professional resume analyzer. Extract only facts present in the resume. "
        "Return valid JSON matching this shape exactly: "
        f"{json.dumps(ANALYSIS_SCHEMA)}\n\nResume:\n{text}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent"
    response = httpx.post(
        url,
        params={"key": settings.AI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    result = json.loads(re.sub(r"^```json\s*|\s*```$", "", result_text.strip()))
    return {
        "summary": str(result.get("summary", "")),
        "technical_skills": result.get("technical_skills", []),
        "soft_skills": result.get("soft_skills", []),
        "education": result.get("education", []),
        "experience": result.get("experience", []),
        "projects": result.get("projects", []),
    }