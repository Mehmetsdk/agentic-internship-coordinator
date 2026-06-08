from crewai import Agent, LLM
from tools import read_pdf


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
        verbose=True,
        allow_delegation=False,
    )
