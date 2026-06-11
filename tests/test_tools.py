"""Unit tests for completeness, rules, and decision tools."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.completeness_checker import check_completeness
from tools.rules_checker import check_university_rules
from tools.decision_maker import make_decision


# ── Helpers ──────────────────────────────────────────────────────────────────

COMPLETE_DATA = (
    "Student name: John Doe | Student ID: 12345 | "
    "Field of study: Computer Engineering | Semester: 3 | "
    "Company: Tech Solutions Ltd. | Supervisor: Jane Smith | "
    "Supervisor email: jane@techsolutions.com | "
    "Internship dates: June 2026 - August 2026"
)

INCOMPLETE_DATA = (
    "Field of study: Computer Engineering | Semester: 3 | "
    "Company: Tech Solutions Ltd."
    # missing: student name, student ID, supervisor name, email, dates
)

NON_COMPLIANT_DATA = (
    "Student name: John Doe | Student ID: 12345 | "
    "Field of study: Philosophy | Semester: 3 | "
    "Company: John's Garage | Supervisor: Bob | "
    "Internship dates: June 2026"
    # invalid field of study, no company registration keyword, no email
)


# ── Completeness Checker Tests ────────────────────────────────────────────────

def test_completeness_pass():
    result = check_completeness.run(COMPLETE_DATA)
    assert "VERDICT: COMPLETE" in result
    assert "[MISSING]" not in result
    print("PASS: test_completeness_pass")


def test_completeness_fail():
    result = check_completeness.run(INCOMPLETE_DATA)
    assert "VERDICT: INCOMPLETE" in result
    assert "[MISSING]" in result
    print("PASS: test_completeness_fail")


# ── University Rules Checker Tests ────────────────────────────────────────────

def test_rules_pass():
    result = check_university_rules.run(COMPLETE_DATA)
    assert "VERDICT: COMPLIANT" in result
    assert "[FAIL]" not in result
    print("PASS: test_rules_pass")


def test_rules_fail():
    result = check_university_rules.run(NON_COMPLIANT_DATA)
    assert "VERDICT: NON-COMPLIANT" in result
    assert "[FAIL]" in result
    print("PASS: test_rules_fail")


# ── Decision Maker Tests ──────────────────────────────────────────────────────

def test_decision_approve():
    completeness = "VERDICT: COMPLETE - All required fields are present."
    rules = "VERDICT: COMPLIANT - Application passes all university rules."
    result = make_decision.run(completeness + "|||" + rules)
    assert "RECOMMENDATION: APPROVE" in result
    print("PASS: test_decision_approve")


def test_decision_reject():
    completeness = "VERDICT: INCOMPLETE\n[MISSING] student_name\n[MISSING] supervisor_email"
    rules = "VERDICT: NON-COMPLIANT\n[FAIL] Field of study does not match."
    result = make_decision.run(completeness + "|||" + rules)
    assert "RECOMMENDATION: REJECT" in result
    print("PASS: test_decision_reject")


def test_decision_clarify_missing_fields():
    completeness = "VERDICT: INCOMPLETE\n[MISSING] supervisor_email"
    rules = "VERDICT: COMPLIANT - Application passes all university rules."
    result = make_decision.run(completeness + "|||" + rules)
    assert "RECOMMENDATION: REQUEST CLARIFICATION" in result
    print("PASS: test_decision_clarify_missing_fields")


def test_decision_clarify_rule_violation():
    completeness = "VERDICT: COMPLETE - All required fields are present."
    rules = "VERDICT: NON-COMPLIANT\n[FAIL] Field of study does not match."
    result = make_decision.run(completeness + "|||" + rules)
    assert "RECOMMENDATION: REQUEST CLARIFICATION" in result
    print("PASS: test_decision_clarify_rule_violation")


# ── Run all ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_completeness_pass()
    test_completeness_fail()
    test_rules_pass()
    test_rules_fail()
    test_decision_approve()
    test_decision_reject()
    test_decision_clarify_missing_fields()
    test_decision_clarify_rule_violation()
    print("\nAll tests passed!")
