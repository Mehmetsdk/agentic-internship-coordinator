"""Belge siniflandirma: hangi PDF rapor, hangisi gunluk."""

import re

from tools.pdf_extract import extract_pdf_text

_DATE_PATTERNS = [
    r"\bDay\s+\d+\b",
    r"\bGun\s+\d+\b",
    r"\bWeek\s+\d+\b",
    r"\bHafta\s+\d+\b",
    r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

_REPORT_PHRASES = [
    r"\bI learned\b",
    r"\bogrendim\b",
    r"\bduring my internship\b",
    r"\bstaj(im)? suresince\b",
    r"\bin this report\b",
    r"\bbu raporda\b",
    r"\bthroughout my internship\b",
    r"\blearning outcomes\b",
    r"\bogrenme ciktilari\b",
]


def _count_matches(text: str, patterns: list) -> int:
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return total


def classify_document_text(text: str) -> str:
    if not text or text.startswith("ERROR:") or text.startswith("WARNING:"):
        return "unreadable"

    date_score = _count_matches(text, _DATE_PATTERNS)
    report_score = _count_matches(text, _REPORT_PHRASES)

    if date_score == 0 and report_score == 0:
        return "unreadable"

    if date_score > report_score:
        return "journal"
    return "report"


def extract_and_classify(pdf_path: str) -> dict:
    text = extract_pdf_text.func(pdf_path)
    classification = classify_document_text(text)
    return {
        "path": pdf_path,
        "text": text,
        "classification": classification,
        "readable": classification != "unreadable",
    }


def classify_submission(pdf_path_1: str, pdf_path_2: str) -> dict:
    doc_1 = extract_and_classify(pdf_path_1)
    doc_2 = extract_and_classify(pdf_path_2)

    warnings = []
    report_doc = None
    journal_doc = None

    for doc in (doc_1, doc_2):
        if doc["classification"] == "report":
            if report_doc is not None:
                warnings.append("Iki belge de rapor olarak siniflandirildi.")
            report_doc = doc
        elif doc["classification"] == "journal":
            if journal_doc is not None:
                warnings.append("Iki belge de gunluk olarak siniflandirildi.")
            journal_doc = doc
        else:
            warnings.append(f"Belge okunamadi: {doc['path']}")

    return {
        "report_text": report_doc["text"] if report_doc else None,
        "report_file": report_doc["path"] if report_doc else None,
        "journal_text": journal_doc["text"] if journal_doc else None,
        "journal_file": journal_doc["path"] if journal_doc else None,
        "submission_metadata": {
            "fully_classified": report_doc is not None and journal_doc is not None,
            "warnings": warnings,
        },
    }
