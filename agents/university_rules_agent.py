from crewai import Agent, LLM
from tools.rules_checker import check_university_rules


def create_university_rules_agent(llm: LLM) -> Agent:
    return Agent(
        role="University Rules Compliance Specialist",
        goal="Validate that the internship application complies with university regulations.",
        backstory=(
            "You are an expert on UTA university internship regulations. "
            "You use the University Rules Checker tool to validate: "
            "field of study eligibility, study cycle, company registration status, "
            "supervisor email presence, and internship dates. "
            "You produce a clear compliance report with passed rules and violations."
        ),
        tools=[check_university_rules],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
