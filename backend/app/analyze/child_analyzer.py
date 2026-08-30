"""Analysis of the document to verify (internally: the child document)."""

from __future__ import annotations

from ..extract import extract_docx
from ..models import DocumentProfile


def analyze_child(data: bytes, file_name: str) -> DocumentProfile:
    """The document to verify is always DOCX, so extraction is exact."""
    return extract_docx(data, file_name)
