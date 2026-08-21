from io import BytesIO

from docx import Document
from pypdf import PdfWriter


def register(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Resume Owner", "email": "resume@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 201


def make_pdf() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)
    return output.getvalue()


def make_docx() -> bytes:
    output = BytesIO()
    document = Document()
    document.add_paragraph("John Doe")
    document.add_paragraph("Skills: Python, FastAPI, SQL, Git")
    document.add_paragraph("Experience")
    document.add_paragraph("Backend Developer - Built APIs")
    document.add_paragraph("Projects")
    document.add_paragraph("Resume Analyzer")
    document.save(output)
    return output.getvalue()


def test_upload_rejects_unsupported_file_type(client):
    register(client)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.jpg", b"not an image", "image/jpeg")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF and DOCX files are supported"


def test_upload_pdf_and_get_resume(client):
    register(client)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.pdf", make_pdf(), "application/pdf")},
    )
    assert response.status_code == 400
    assert "readable text" in response.json()["detail"]


def test_upload_docx_analyze_and_get_analysis(client, monkeypatch):
    from app.routes import resumes

    register(client)
    upload = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.docx", make_docx(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert upload.status_code == 201
    resume = upload.json()
    assert resume["raw_text"]

    monkeypatch.setattr(resumes, "analyze_resume", lambda text: {
        "summary": "Backend developer with Python experience.",
        "technical_skills": ["Python", "FastAPI", "SQL", "Git"],
        "soft_skills": [],
        "education": [],
        "experience": [{"company": "", "position": "Backend Developer", "duration": "", "responsibilities": []}],
        "projects": [{"name": "Resume Analyzer", "description": "", "technologies": ["Python"]}],
    })
    analysis = client.post(f"/api/resumes/{resume['id']}/analyze")
    assert analysis.status_code == 200
    assert "Python" in analysis.json()["technical_skills"]
    assert analysis.json()["projects"]

    fetched = client.get(f"/api/resumes/{resume['id']}/analysis")
    assert fetched.status_code == 200
    assert fetched.json()["resume_id"] == resume["id"]