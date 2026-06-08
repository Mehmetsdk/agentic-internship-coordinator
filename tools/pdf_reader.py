import pdfplumber
from crewai.tools import tool


@tool("PDF Reader")
def read_pdf(pdf_path: str) -> str:
    """
    Reads a PDF file and extracts all text content from it.
    Use this tool to extract text from internship application PDF forms.
    Input: the file path to the PDF.
    Output: the full extracted text from the PDF.
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i + 1} ---\n"
                    text += page_text
        if not text.strip():
            return "ERROR: No text could be extracted from the PDF. It may be a scanned image."
        return text.strip()
    except FileNotFoundError:
        return f"ERROR: PDF file not found at path: {pdf_path}"
    except Exception as e:
        return f"ERROR reading PDF: {str(e)}"
