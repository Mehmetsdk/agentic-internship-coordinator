from crewai import Agent, LLM
from tools.completeness_checker import check_completeness


def create_completeness_validation_agent(llm: LLM) -> Agent:
    return Agent(
        role="Completeness Validation Specialist",
        goal="Check whether all required fields in the internship application are filled in correctly.",
        backstory=(
            "You carefully review extracted application data to ensure nothing is missing. "
            "You use the Completeness Checker tool to verify all required fields: "
            "student name, student ID, field of study, semester, company name, "
            "supervisor name, supervisor email, and internship dates. "
            "You produce a clear report listing present and missing fields."
        ),
        tools=[check_completeness],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
