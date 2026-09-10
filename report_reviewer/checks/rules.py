"""Deterministic verification checks for report + journal submissions.

No LLM used anywhere in this module — every check is plain Python logic
on extracted text. This is the single source of truth for PASS/WARNING/
FAIL decisions; the advisor (LLM) layer must never override these results.
"""

import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_DATE_PATTERNS = [
    r"(\d{1,2})[./](\d{1,2})[./](\d{2,4})",
    r"(\d{4})-(\d{2})-(\d{2})",
]

_HOURS_PATTERN = r"(\d+(?:\.\d+)?)\s*hours?"
_DEFAULT_HOURS_PER_DAY = 8
_MIN_REQUIRED_DAYS = 20

_REQUIRED_REPORT_KEYWORDS = ["learn", "intern"]


def _extract_dates(text: str) -> list:
    dates = []
    for pattern in _DATE_PATTERNS:
        for match in re.finditer(pattern, text):
            groups = match.groups()
            try:
                if len(groups[0]) == 4:
                    year, month, day = groups
                else:
                    day, month, year = groups
                y = int(year) if len(year) == 4 else 2000 + int(year)
                dates.append(datetime(y, int(month), int(day)))
            except (ValueError, IndexError):
                continue
    unique = sorted(set(dates))
    logger.debug("_extract_dates -> found %d dates: %s", len(unique), unique)
    return unique


def _extract_journal_entry_count(text: str) -> int:
    day_markers = re.findall(r"\bDay\s+\d+\b", text, flags=re.IGNORECASE)
    if day_markers:
        cnt = len(set(day_markers))
        logger.debug("_extract_journal_entry_count -> day_markers detected: %s (count=%d)", day_markers, cnt)
        return cnt
    cnt = len(_extract_dates(text))
    logger.debug("_extract_journal_entry_count -> date-based count=%d", cnt)
    return cnt


def _extract_total_hours(text: str):
    matches = re.findall(_HOURS_PATTERN, text, flags=re.IGNORECASE)
    if matches:
        vals = [float(m) for m in matches]
        total = sum(vals)
        logger.debug("_extract_total_hours -> found matches=%s total=%s", vals, total)
        return total
    return None


def check_date_consistency(report_text: str, journal_text: str) -> dict:
    journal_dates = _extract_dates(journal_text)
    logger.debug("check_date_consistency -> journal_dates=%s", journal_dates)
    if not journal_dates:
        return {"code": "DATE_CONSISTENCY", "status": "WARNING",
                "message": "No dates could be extracted from the journal."}

    today = datetime.now()
    future_dates = [d for d in journal_dates if d > today]
    if future_dates:
        return {"code": "DATE_CONSISTENCY", "status": "FAIL",
                "message": f"Journal contains {len(future_dates)} future date(s): "
                           f"{', '.join(d.strftime('%d.%m.%Y') for d in future_dates[:3])}."}
    span_days = (journal_dates[-1] - journal_dates[0]).days
    logger.debug("check_date_consistency -> span_days=%s first=%s last=%s", span_days, journal_dates[0], journal_dates[-1])
    return {"code": "DATE_CONSISTENCY", "status": "PASS",
            "message": f"Journal dates span {span_days} days, "
                       f"from {journal_dates[0].strftime('%d.%m.%Y')} "
                       f"to {journal_dates[-1].strftime('%d.%m.%Y')}. No future dates found."}


def check_journal_hours(journal_text: str) -> dict:
    entry_count = _extract_journal_entry_count(journal_text)
    total_hours = _extract_total_hours(journal_text)
    logger.debug("check_journal_hours -> entry_count=%s total_hours=%s", entry_count, total_hours)

    if total_hours is None:
        if entry_count == 0:
            return {"code": "JOURNAL_HOURS", "status": "WARNING",
                    "message": "Could not determine journal entry count or hours.", "value": 0}
        total_hours = entry_count * _DEFAULT_HOURS_PER_DAY
    threshold = _MIN_REQUIRED_DAYS * _DEFAULT_HOURS_PER_DAY
    status = "PASS" if total_hours >= threshold else "WARNING"
    return {"code": "JOURNAL_HOURS", "status": status,
            "message": f"{entry_count} journal entries found, "
                       f"estimated {total_hours:.0f} total hours "
                       f"(minimum expected: {_MIN_REQUIRED_DAYS} days / {threshold} hours).",
            "value": total_hours}


def check_name_consistency(report_text: str, journal_text: str, student_name: str) -> dict:
    if not student_name.strip():
        return {"code": "NAME_CONSISTENCY", "status": "WARNING",
                "message": "No student name provided to check against."}

    name_parts = [p.lower() for p in student_name.strip().split() if len(p) > 1]
    report_lower = report_text.lower()
    journal_lower = journal_text.lower()

    in_report = any(part in report_lower for part in name_parts)
    in_journal = any(part in journal_lower for part in name_parts)
    logger.debug("check_name_consistency -> name_parts=%s in_report=%s in_journal=%s", name_parts, in_report, in_journal)

    if in_report and in_journal:
        return {"code": "NAME_CONSISTENCY", "status": "PASS",
                "message": f"Student name '{student_name}' found in both documents."}

    missing = []
    if not in_report:
        missing.append("report")
    if not in_journal:
        missing.append("journal")
    return {"code": "NAME_CONSISTENCY", "status": "WARNING",
            "message": f"Student name '{student_name}' not found in: {', '.join(missing)}."}


def check_required_content(report_text: str) -> dict:
    report_lower = report_text.lower()
    missing = [kw for kw in _REQUIRED_REPORT_KEYWORDS if kw not in report_lower]
    logger.debug("check_required_content -> missing_keywords=%s", missing)
    if missing:
        return {"code": "REQUIRED_CONTENT", "status": "WARNING",
                "message": f"Report may be missing expected content related to: {', '.join(missing)}."}
    return {"code": "REQUIRED_CONTENT", "status": "PASS",
            "message": "Report contains expected learning-outcome language."}


def run_all_checks(report_text: str, journal_text: str, student_name: str = "") -> dict:
    # Guard against missing document text to avoid downstream NoneType errors
    if not report_text or not journal_text:
        logger.debug("run_all_checks -> missing report_text or journal_text")
        return {
            "overall_status": "FAILED",
            "checks": [],
            "error": "One or both documents could not be read or are empty.",
        }
    checks = [
        check_date_consistency(report_text, journal_text),
        check_journal_hours(journal_text),
        check_name_consistency(report_text, journal_text, student_name),
        check_required_content(report_text),
    ]

    passed = sum(1 for c in checks if c["status"] == "PASS")
    warnings = sum(1 for c in checks if c["status"] == "WARNING")
    failed = sum(1 for c in checks if c["status"] == "FAIL")

    if failed > 0:
        overall = "REJECTED"
    elif warnings > 0:
        overall = "REQUEST_CLARIFICATION"
    else:
        overall = "APPROVED"

    return {
        "checks": checks,
        "passed_count": passed,
        "warning_count": warnings,
        "failed_count": failed,
        "overall_status": overall,
    }
