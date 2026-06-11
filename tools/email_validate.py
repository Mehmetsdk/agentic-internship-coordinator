"""Email and PDF path validation tools for Agent 1."""

import os
import re

from crewai.tools import tool

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@tool("Validate Email")
def validate_email(email: str) -> str:
    """Validate that a string is a well-formed email address."""
    if not email or not str(email).strip():
        return "INVALID: Email is empty."
    email = str(email).strip()
    if not _EMAIL_RE.match(email):
        return f"INVALID: '{email}' is not a valid email format."
    return f"VALID: Email '{email}' has acceptable format."


@tool("Validate PDF Path")
def validate_pdf_path(path: str) -> str:
    """Validate that a PDF file exists at the given path and is readable."""
    if not path or not str(path).strip():
        return "INVALID: PDF path is empty."
    path = str(path).strip()
    if not os.path.isfile(path):
        return f"INVALID: No file found at '{path}'."
    if not path.lower().endswith(".pdf"):
        return f"INVALID: File at '{path}' is not a .pdf extension."
    if not os.access(path, os.R_OK):
        return f"INVALID: File at '{path}' is not readable."
    return f"VALID: PDF exists and is readable at '{path}'."
