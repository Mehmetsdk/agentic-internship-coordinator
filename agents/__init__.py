"""Agent factory exports for the internship coordinator pipeline."""

from crewai import Agent, LLM

from agents.completeness_validation import create_completeness_validation_agent
from agents.document_extraction_agent import create_document_extraction_agent
from agents.email_intake_agent import create_email_intake_agent
from agents.supervisor_verification_agent import create_supervisor_verification_agent
from agents.university_rules import create_university_rules_agent


def create_decision_recommendation_agent(llm: LLM) -> Agent:
    return Agent(
        role="Decision Recommendation Specialist",
        goal="Recommend APPROVE, REJECT, or REQUEST CLARIFICATION for the coordinator.",
        backstory="You synthesize all prior agent outputs into a final actionable recommendation.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


__all__ = [
    "create_email_intake_agent",
    "create_document_extraction_agent",
    "create_completeness_validation_agent",
    "create_university_rules_agent",
    "create_supervisor_verification_agent",
    "create_decision_recommendation_agent",
]
