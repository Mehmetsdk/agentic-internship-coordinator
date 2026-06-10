"""Email template loading tools for supervisor verification and outreach."""

from pathlib import Path

from crewai.tools import tool

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_AVAILABLE_TEMPLATES = {
    "application_received": "application_received_email.txt",
    "missing_information": "missing_information_email.txt",
    "verification_request": "verification_request_email.txt",
}


def _render_template(template_name: str, placeholders: dict[str, str]) -> str:
    filename = _AVAILABLE_TEMPLATES.get(template_name)
    if not filename:
        available = ", ".join(sorted(_AVAILABLE_TEMPLATES))
        return f"ERROR: Unknown template '{template_name}'. Available: {available}"

    path = _TEMPLATES_DIR / filename
    if not path.is_file():
        return f"ERROR: Template file not found at '{path}'."

    content = path.read_text(encoding="utf-8")
    for key, value in placeholders.items():
        content = content.replace(f"{{{{{key}}}}}", value or "")
    return content


@tool("Load Email Template")
def load_email_template(template_name: str, placeholders_json: str = "{}") -> str:
    """Load and render an email template with optional placeholders.

    template_name: one of application_received, missing_information, verification_request
    placeholders_json: JSON object string, e.g. {"student_name": "Jane Doe"}
    """
    import json

    try:
        placeholders = json.loads(placeholders_json) if placeholders_json.strip() else {}
    except json.JSONDecodeError as exc:
        return f"ERROR: Invalid placeholders_json: {exc}"

    if not isinstance(placeholders, dict):
        return "ERROR: placeholders_json must decode to a JSON object."

    normalized = {str(k): str(v) for k, v in placeholders.items()}
    return _render_template(template_name.strip().lower(), normalized)
