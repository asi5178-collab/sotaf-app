#!/usr/bin/env python3
"""Extract plain text from uploaded PDF / Word files."""
import io

from pypdf import PdfReader
from docx import Document

MAX_CHARS_PER_FILE = 20000


def extract_text(filename: str, data: bytes) -> str:
    """Extract text from a PDF or DOCX file's raw bytes. Returns '' on unsupported type."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        text = _extract_pdf(data)
    elif lower.endswith(".docx"):
        text = _extract_docx(data)
    else:
        return ""

    if len(text) > MAX_CHARS_PER_FILE:
        text = text[:MAX_CHARS_PER_FILE] + "\n[...טקסט קוצץ...]"
    return text


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)
