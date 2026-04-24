from __future__ import annotations

import io
from typing import BinaryIO

import pdfplumber


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Extract plain text from a PDF resume (best-effort)."""
    buf: BinaryIO = io.BytesIO(data)
    parts: list[str] = []
    with pdfplumber.open(buf) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
    return "\n\n".join(parts).strip()
