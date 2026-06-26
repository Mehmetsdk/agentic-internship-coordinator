"""PDF anonymization tool — strips PII before agents process the document."""

import json
import sys
import tempfile
from pathlib import Path

from crewai.tools import tool

ANONYMIZER_ROOT = next(
    (p for p in [
        Path("/app/PDF---Anonymizer"),
        Path(__file__).parent.parent.parent / "PDF---Anonymizer",
    ] if p.exists()),
    Path(__file__).parent.parent.parent / "PDF---Anonymizer",
)

for _p in [
    ANONYMIZER_ROOT / "extractor",
    ANONYMIZER_ROOT / "fake_generator",
    ANONYMIZER_ROOT / "reconstructor",
    ANONYMIZER_ROOT,
]:
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)


def anonymize_pdf_file(pdf_path: str) -> str:
    """
    Anonymize a PDF file — callable directly (not a CrewAI tool).
    Returns path to anonymized PDF, or original path if no PII found / on error.
    """
    pdf_path = str(pdf_path).strip()
    src = Path(pdf_path)
    if not src.exists():
        return pdf_path

    try:
        from pdf_extractor import extract_text_with_layout, is_scanned_pdf, ocr_pdf
        from pii_detector import detect_pii
        from fake_data_generator import build_replacements
        from reconstructor import reconstruct_pdf
        from pipeline import _build_anonymization_map
    except ImportError as e:
        print(f"[anonymizer] WARNING: Could not import modules: {e}")
        return pdf_path

    try:
        work_dir = Path(tempfile.mkdtemp())
        out_path = work_dir / f"{src.stem}_anonymized.pdf"

        if is_scanned_pdf(str(src)):
            layout = ocr_pdf(str(src))
        else:
            layout = extract_text_with_layout(str(src))

        pii_result = detect_pii(layout)
        detections = pii_result["detections"]

        if not detections:
            return pdf_path  # no PII, use original as-is

        replacements, _ = build_replacements(detections)
        anon_map = _build_anonymization_map(replacements, detections)

        anon_map_path = work_dir / "anon_map.json"
        anon_map_path.write_text(
            json.dumps(anon_map, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        reconstruct_pdf(str(src), str(anon_map_path), str(out_path))
        return str(out_path)

    except Exception as e:
        print(f"[anonymizer] WARNING: Anonymization failed, using original: {e}")
        return pdf_path


@tool("Anonymize PDF")
def anonymize_pdf(pdf_path: str) -> str:
    """
    Anonymize a PDF by replacing all PII (names, IDs, emails, phones, IBANs)
    with realistic fake values. Returns the path to the anonymized PDF.
    """
    result = anonymize_pdf_file(pdf_path)
    if result == str(pdf_path).strip():
        return f"NO_PII_FOUND: {pdf_path} (no sensitive data detected, original kept)"
    return result
