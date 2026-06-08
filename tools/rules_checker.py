from crewai.tools import tool


UNIVERSITY_RULES = {
    "min_internship_days": 20,
    "valid_fields_of_study": [
        "computer engineering",
        "software engineering",
        "electrical engineering",
        "mechanical engineering",
        "industrial engineering",
        "civil engineering",
    ],
    "valid_cycles": ["I", "II", "1", "2"],
    "required_company_keywords": ["ltd", "inc", "llc", "a.s", "a.ş", "gmbh", "corp", "company", "co."],
}


@tool("University Rules Checker")
def check_university_rules(extracted_data: str) -> str:
    """
    Validates the internship application against university regulations.
    Input: extracted text/data from the internship application PDF.
    Output: a compliance report listing passed and failed rules.
    """
    extracted_lower = extracted_data.lower()

    passed = []
    violations = []

    # Rule 1: Field of study must match engineering programs
    if any(field in extracted_lower for field in UNIVERSITY_RULES["valid_fields_of_study"]):
        passed.append("Field of study is a valid engineering program.")
    else:
        violations.append("Field of study does not match a recognized engineering program.")

    # Rule 2: Valid study cycle (I or II)
    if any(cycle.lower() in extracted_lower for cycle in UNIVERSITY_RULES["valid_cycles"]):
        passed.append("Study cycle (I/II) is valid.")
    else:
        violations.append("Study cycle (I/II) is missing or invalid.")

    # Rule 3: Company appears to be a registered organization
    if any(kw in extracted_lower for kw in UNIVERSITY_RULES["required_company_keywords"]):
        passed.append("Company appears to be a registered organization.")
    else:
        violations.append("Company name does not indicate a registered organization (missing: Ltd, Inc, A.Ş., etc.).")

    # Rule 4: Supervisor email present
    if "@" in extracted_lower:
        passed.append("Supervisor email address is present.")
    else:
        violations.append("Supervisor email address is missing.")

    # Rule 5: Internship dates mentioned
    date_keywords = ["2025", "2026", "january", "february", "march", "april", "may",
                     "june", "july", "august", "september", "october", "november", "december",
                     "ocak", "subat", "mart", "nisan", "mayis", "haziran",
                     "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"]
    if any(kw in extracted_lower for kw in date_keywords):
        passed.append("Internship dates are mentioned.")
    else:
        violations.append("Internship dates are not clearly stated.")

    # Build report
    report = "=== UNIVERSITY RULES COMPLIANCE REPORT ===\n\n"

    report += f"PASSED RULES ({len(passed)}):\n"
    for r in passed:
        report += f"  [PASS] {r}\n"

    if violations:
        report += f"\nVIOLATIONS ({len(violations)}):\n"
        for v in violations:
            report += f"  [FAIL] {v}\n"
        report += "\nVERDICT: NON-COMPLIANT - Application has rule violations.\n"
    else:
        report += "\nVERDICT: COMPLIANT - Application passes all university rules.\n"

    return report
