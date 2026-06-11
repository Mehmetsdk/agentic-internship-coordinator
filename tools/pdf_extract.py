"""PDF text extraction tool for Agent 2."""

from crewai.tools import tool


@tool("Extract PDF Text")
def extract_pdf_text(pdf_path: str) -> str:
    """Extract all text content from a PDF file using pdfplumber."""
    if not pdf_path or not str(pdf_path).strip():
        return "ERROR: PDF path is empty."
    pdf_path = str(pdf_path).strip()
    try:
        import pdfplumber
    except ImportError:
        return "ERROR: pdfplumber is not installed."

    try:
        pages: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return "ERROR: PDF contains no pages."
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append(f"--- Page {i} ---\n{text}")
        combined = "\n\n".join(pages).strip()
        if not combined:
            return (
                f"WARNING: PDF opened successfully at '{pdf_path}' "
                "but no extractable text was found (may be scanned/image-only)."
            )
        return combined
    except FileNotFoundError:
        return f"ERROR: File not found at '{pdf_path}'."
    except PermissionError:
        return f"ERROR: Permission denied reading '{pdf_path}'."
    except Exception as exc:
        return f"ERROR: Failed to extract text from '{pdf_path}': {exc}"
