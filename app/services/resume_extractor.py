from io import BytesIO

from docx import Document
from pypdf import PdfReader


class ResumeExtractionError(ValueError):
    pass


def extract_pdf(content: bytes) -> str:
    try:
        document = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in document.pages).strip()
    except Exception as exc:
        raise ResumeExtractionError("The PDF file is corrupted or unreadable") from exc


def extract_docx(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
        return "\n".join(text for text in paragraphs if text)
    except Exception as exc:
        raise ResumeExtractionError("The DOCX file is corrupted or unreadable") from exc


def extract_resume_text(filename: str, content: bytes) -> str:
    extension = filename.lower().rsplit(".", 1)[-1]
    text = extract_pdf(content) if extension == "pdf" else extract_docx(content)
    if not text:
        raise ResumeExtractionError("The resume does not contain readable text")
    return text