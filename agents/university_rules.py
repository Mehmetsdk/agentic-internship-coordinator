"""Agent 4: University Rules Specialist."""

from crewai import Agent, LLM


def create_university_rules_agent(llm: LLM) -> Agent:
    return Agent(
        role="University Rules Specialist",
        goal=(
            "Validate internship applications against university requirements."
        ),
        backstory=(
            "You review extracted application data and enforce official university "
            "internship regulations. You detect rule violations and generate a "
            "structured validation report. Apply these rules:\n"
            "- Internship duration must be at least 20 working days\n"
            "- Supervisor email must be present\n"
            "- Company name must be present\n"
            "- Student ID must be present\n\n"
            "Treat values such as 'missing', 'unclear', or blank entries as "
            "violations where a field is required. Your final response must use "
            "exactly this format:\n\n"
            "RULE_VALIDATION_STATUS:\n"
            "PASS | FAIL\n\n"
            "VIOLATIONS:\n"
            "* violation description\n"
            "* violation description\n\n"
            "NOTES: ...\n\n"
            "If no violations exist, respond with:\n\n"
            "RULE_VALIDATION_STATUS: PASS\n"
            "VIOLATIONS: NONE"
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
