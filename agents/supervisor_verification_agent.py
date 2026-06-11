"""Agent 5: Supervisor Verification Specialist."""

from crewai import Agent, LLM

from tools.template_loader import load_email_template


def create_supervisor_verification_agent(llm: LLM) -> Agent:
    return Agent(
        role="Supervisor Verification Specialist",
        goal=(
            "Determine whether internship applications require additional "
            "supervisor verification."
        ),
        backstory=(
            "You review supervisor and company information from extracted "
            "application data and prior validation reports. You detect missing "
            "supervisor details, suspicious or unverifiable contact information "
            "(e.g. personal webmail without company domain, generic titles, "
            "unknown organizations), and decide whether outreach is required. "
            "When verification is needed, use the Load Email Template tool with "
            "template_name 'verification_request' and placeholders for "
            "student_name, company_name, and supervisor_name. Available "
            "templates live under templates/: application_received_email.txt, "
            "missing_information_email.txt, verification_request_email.txt. "
            "Your final response must use exactly this format:\n\n"
            "VERIFICATION_STATUS:\n"
            "REQUIRES_VERIFICATION\n"
            "OR\n"
            "NOT_REQUIRED\n\n"
            "REASON:\n"
            "...\n\n"
            "EMAIL_TEMPLATE_REQUIRED:\n"
            "YES\n"
            "OR\n"
            "NO"
        ),
        llm=llm,
        tools=[load_email_template],
        verbose=True,
        allow_delegation=False,
    )
