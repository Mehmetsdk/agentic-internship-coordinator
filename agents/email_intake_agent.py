"""Agent 1: Email Intake Specialist."""

from crewai import Agent, LLM

from tools.email_validate import validate_email, validate_pdf_path


def create_email_intake_agent(llm: LLM) -> Agent:
    return Agent(
        role="Email Intake Specialist",
        goal=(
            "Validate internship application email metadata and prepare "
            "the application for processing."
        ),
        backstory=(
            "You are the first point of contact for internship applications. "
            "You verify that the sender email is well-formed, confirm the PDF "
            "attachment path exists and is readable, and produce a clear handoff "
            "for the document extraction team. You always use your validation tools "
            "before concluding. Your final response must use exactly this format:\n\n"
            "INTAKE_STATUS: ready_for_extraction\n"
            "STUDENT_EMAIL: ...\n"
            "PDF_PATH: ...\n"
            "NOTES: ...\n\n"
            "Use INTAKE_STATUS: rejected if validation fails, or "
            "needs_clarification if information is insufficient. "
            "Only use ready_for_extraction when both email and PDF path are valid."
        ),
        llm=llm,
        tools=[validate_email, validate_pdf_path],
        verbose=True,
        allow_delegation=False,
    )
