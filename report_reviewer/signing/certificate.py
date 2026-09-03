"""Sertifika PDF uretici - staj rapor incelemesi tamamlandiginda cagrilir.

NOT: Bu, gecici bir uygulama. Mehmet'in pdf_backend.py fonksiyonlari
gelince, gercek imza gorseli (el yazisi imza) yerlestirme burada
entegre edilecek. Simdilik hash + metin tabanli bir sertifika uretiyor,
boylece dashboard entegrasyonu ve akis testi Mehmet'i beklemeden yapilabiliyor.
"""

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from report_reviewer.signing.hashing import compute_package_hash

CERTIFICATES_DIR = Path(__file__).resolve().parent.parent.parent / "logs" / "certificates"


def generate_certificate(
    student_name: str,
    student_email: str,
    report_path: str,
    journal_path: str,
    coordinator_name: str,
) -> dict:
    """
    Iki belgeyi hash'ler, bir tamamlama sertifikasi PDF'i uretir.
    Donen dict: {certificate_path, package_hash, report_hash, journal_hash}
    """
    hashes = compute_package_hash(report_path, journal_path)
    issued_at = datetime.now()

    CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
    safe_email = student_email.replace("@", "_at_").replace(".", "_")
    ts = issued_at.strftime("%Y%m%d_%H%M%S")
    cert_path = CERTIFICATES_DIR / f"certificate_{safe_email}_{ts}.pdf"

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 20, "Internship Completion Certificate", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, (
        "This certifies that the internship completion report and journal "
        "submitted by the student below have been reviewed and verified as "
        "internally consistent by the university coordinator.\n\n"
        "This attests to the completeness and internal consistency of the "
        "submitted record. It is not an assessment of the quality of the "
        "work performed."
    ))
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Student:", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"  {student_name} ({student_email})", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Reviewed and signed by:", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"  {coordinator_name}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Issued:", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"  {issued_at.strftime('%d %B %Y, %H:%M')}", ln=True)
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Document verification (SHA-256):", ln=True)
    pdf.set_font("Courier", "", 8)
    pdf.multi_cell(0, 5, (
        f"Report hash:   {hashes['report_hash']}\n"
        f"Journal hash:  {hashes['journal_hash']}\n"
        f"Package hash:  {hashes['package_hash']}"
    ))

    pdf.output(str(cert_path))

    return {
        "certificate_path": str(cert_path),
        "package_hash": hashes["package_hash"],
        "report_hash": hashes["report_hash"],
        "journal_hash": hashes["journal_hash"],
        "issued_at": issued_at.isoformat(),
    }
