# Agent Input/Output Contracts

## Agent 3 — Completeness Validation Agent

**Tool:** `check_completeness`

**Input:**
```
Extracted text from the internship application PDF (plain string).
Example: "Student name: John Doe | Student ID: 12345 | ..."
```

**Output:**
```
=== COMPLETENESS REPORT ===

PRESENT FIELDS (8/8):
  [OK] student_name
  ...

VERDICT: COMPLETE - All required fields are present.
```
or
```
MISSING FIELDS (2/8):
  [MISSING] supervisor_email
  [MISSING] internship_dates

VERDICT: INCOMPLETE - Clarification required.
```

---

## Agent 4 — University Rules Agent

**Tool:** `check_university_rules`

**Input:**
```
Extracted text from the internship application PDF (plain string).
```

**Output:**
```
=== UNIVERSITY RULES COMPLIANCE REPORT ===

PASSED RULES (5):
  [PASS] Field of study is a valid engineering program.
  ...

VERDICT: COMPLIANT - Application passes all university rules.
```
or
```
VIOLATIONS (2):
  [FAIL] Field of study does not match a recognized engineering program.
  [FAIL] Supervisor email address is missing.

VERDICT: NON-COMPLIANT - Application has rule violations.
```

---

## Agent 6 — Decision Recommendation Agent

**Tool:** `make_decision`

**Input:**
```
<completeness_report>|||<rules_report>
```

**Output:**
```
=== DECISION RECOMMENDATION ===

RECOMMENDATION: APPROVE | REJECT | REQUEST CLARIFICATION

JUSTIFICATION:
...

NOTE: Final decision must be approved by the human coordinator.
```
