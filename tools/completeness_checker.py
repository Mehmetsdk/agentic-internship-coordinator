from crewai.tools import tool


REQUIRED_FIELDS = [
    "student_name",
    "student_id",
    "field_of_study",
    "semester",
    "company_name",
    "supervisor_name",
    "supervisor_email",
    "internship_dates",
]


@tool("Completeness Checker")
def check_completeness(extracted_data: str) -> str:
    """
    Checks whether all required fields are present in the extracted application data.
    Input: extracted text/data from the internship application PDF.
    Output: a completeness report listing present and missing fields.
    """
    extracted_lower = extracted_data.lower()

    present = []
    missing = []

    field_keywords = {
        "student_name":     ["student name", "name and surname", "student's name"],
        "student_id":       ["student id", "student number", "id number"],
        "field_of_study":   ["field of study", "program", "department", "computer engineering", "engineering"],
        "semester":         ["semester"],
        "company_name":     ["company", "employer", "workplace", "organization"],
        "supervisor_name":  ["supervisor name", "supervisor", "manager", "mentor"],
        "supervisor_email": ["supervisor email", "email", "@"],
        "internship_dates": ["internship date", "start date", "end date", "period", "from", "to", "duration"],
    }

    for field, keywords in field_keywords.items():
        if any(kw in extracted_lower for kw in keywords):
            present.append(field)
        else:
            missing.append(field)

    report = "=== COMPLETENESS REPORT ===\n\n"

    report += f"PRESENT FIELDS ({len(present)}/{len(REQUIRED_FIELDS)}):\n"
    for f in present:
        report += f"  [OK] {f}\n"

    if missing:
        report += f"\nMISSING FIELDS ({len(missing)}/{len(REQUIRED_FIELDS)}):\n"
        for f in missing:
            report += f"  [MISSING] {f}\n"
        report += "\nVERDICT: INCOMPLETE - Clarification required.\n"
    else:
        report += "\nVERDICT: COMPLETE - All required fields are present.\n"

    return report
