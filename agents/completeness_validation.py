"""Agent 3: Completeness Validation Specialist."""

from crewai import Agent, LLM


def create_completeness_validation_agent(llm: LLM) -> Agent:
    return Agent(
        role="Completeness Validation Specialist",
        goal=(
            "Verify that all required internship application fields are present."
        ),
        backstory=(
            "You inspect structured extraction output from the document extraction "
            "team and determine whether the application contains every required "
            "field. You detect missing information, flag incomplete applications, "
            "and produce a clear validation report. Treat values such as 'missing', "
            "'unclear', or blank entries as absent fields. Your final response must "
            "use exactly this format:\n\n"
            "COMPLETENESS_STATUS: COMPLETE | INCOMPLETE\n\n"
            "MISSING_FIELDS:\n"
            "* field_name\n"
            "* field_name\n\n"
            "NOTES: ...\n\n"
            "If all required fields exist, respond with:\n\n"
            "COMPLETENESS_STATUS: COMPLETE\n"
            "MISSING_FIELDS: NONE\n\n"
            "Required fields: student_name, student_id, company_name, "
            "supervisor_name, supervisor_email, internship_dates."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
