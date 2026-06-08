from crewai import Agent, LLM
from tools.decision_maker import make_decision


def create_decision_recommendation_agent(llm: LLM) -> Agent:
    return Agent(
        role="Decision Recommendation Specialist",
        goal="Produce a final APPROVE / REJECT / REQUEST CLARIFICATION recommendation for the human coordinator.",
        backstory=(
            "You are the final step in the internship application review pipeline. "
            "You receive the completeness report and the university rules compliance report, "
            "then use the Decision Maker tool to produce a clear, well-justified recommendation. "
            "You never make the final decision yourself — the human coordinator has the last word."
        ),
        tools=[make_decision],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
