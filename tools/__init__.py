"""Tools package for internship coordinator agents.

Consolidated exports for email validation, PDF extraction, and email templates.
"""

from tools.email_validate import validate_email, validate_pdf_path
from tools.pdf_extract import extract_pdf_text
from tools.template_loader import load_email_template

__all__ = [
    "validate_email",
    "validate_pdf_path",
    "extract_pdf_text",
    "load_email_template",
]
