from crewai import Agent, LLM
from tools import read_pdf
"""Agent 2: Document Extraction Specialist."""

from crewai import Agent, LLM

from tools.pdf_extract import extract_pdf_text


def create_document_extraction_agent(llm: LLM) -> Agent:
    return Agent(
        role="Document Extraction Specialist",
        goal="Extract all relevant student and company information from internship application PDFs.",
        backstory=(
            "You are an expert at reading and parsing internship application forms. "
            "You use the PDF Reader tool to open the file and extract: "
            "student name, student ID, field of study, semester, company name, "
            "supervisor name, supervisor email, and internship dates."
        ),
        tools=[read_pdf],
        llm=llm,
        goal="Extract structured internship application information from PDF files.",
        backstory=(
            "You specialize in reading internship application PDFs. "
            "You always call the PDF text extraction tool first, then parse the "
            "raw text to identify application fields. If a field is missing or "
            "unclear in the document, write 'missing' or 'unclear' for that field. "
            "Do not invent data. Your final response must use exactly this format:\n\n"
            "STUDENT_NAME:\n"
            "STUDENT_ID:\n"
            "FIELD_OF_STUDY:\n"
            "SEMESTER:\n"
            "COMPANY_NAME:\n"
            "SUPERVISOR_NAME:\n"
            "SUPERVISOR_EMAIL:\n"
            "INTERNSHIP_DATES:"
        ),
        llm=llm,
        tools=[extract_pdf_text],
        verbose=True,
        allow_delegation=False,
    )
