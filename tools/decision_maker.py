from crewai.tools import tool


@tool("Decision Maker")
def make_decision(reports: str) -> str:
    """
    Produces a final recommendation based on completeness and rules reports.
    Input: both reports combined as a single string separated by '|||'.
    Format: '<completeness_report>|||<rules_report>'
    Output: APPROVE, REJECT, or REQUEST CLARIFICATION with justification.
    """
    parts = reports.split("|||")
    if len(parts) == 2:
        completeness = parts[0].strip()
        rules = parts[1].strip()
    else:
        completeness = reports
        rules = reports

    completeness_lower = completeness.lower()
    rules_lower = rules.lower()

    is_complete = "verdict: complete" in completeness_lower
    is_compliant = "verdict: compliant" in rules_lower

    missing_fields = []
    violations = []

    for line in completeness.splitlines():
        if "[missing]" in line.lower():
            missing_fields.append(line.strip())

    for line in rules.splitlines():
        if "[fail]" in line.lower():
            violations.append(line.strip())

    report = "=== DECISION RECOMMENDATION ===\n\n"

    if is_complete and is_compliant:
        report += "RECOMMENDATION: APPROVE\n\n"
        report += "JUSTIFICATION:\n"
        report += "All required fields are present and the application fully complies\n"
        report += "with university internship regulations. Ready for coordinator approval.\n"

    elif not is_complete and not is_compliant:
        report += "RECOMMENDATION: REJECT\n\n"
        report += "JUSTIFICATION:\n"
        report += "The application has both missing fields and rule violations.\n\n"
        if missing_fields:
            report += "Missing fields:\n"
            for f in missing_fields:
                report += f"  - {f}\n"
        if violations:
            report += "Rule violations:\n"
            for v in violations:
                report += f"  - {v}\n"

    elif not is_complete:
        report += "RECOMMENDATION: REQUEST CLARIFICATION\n\n"
        report += "JUSTIFICATION:\n"
        report += "The application is missing required fields. "
        report += "Please ask the student to provide the following:\n"
        for f in missing_fields:
            report += f"  - {f}\n"

    else:
        report += "RECOMMENDATION: REQUEST CLARIFICATION\n\n"
        report += "JUSTIFICATION:\n"
        report += "The application has rule violations that must be resolved:\n"
        for v in violations:
            report += f"  - {v}\n"

    report += "\nNOTE: Final decision must be approved by the human coordinator.\n"
    return report
