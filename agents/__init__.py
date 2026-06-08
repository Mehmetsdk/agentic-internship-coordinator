"""Agent factory exports for the internship coordinator pipeline."""

from crewai import Agent, LLM

from agents.document_extraction import create_document_extraction_agent
from agents.email_intake import create_email_intake_agent


def create_completeness_validation_agent(llm: LLM) -> Agent:
    return Agent(
        role="Completeness Validation Specialist",
        goal="Check extracted application data for missing or incomplete fields.",
        backstory="You review structured extraction output and report field-level completeness.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_university_rules_agent(llm: LLM) -> Agent:
    return Agent(
        role="University Rules Specialist",
        goal="Validate applications against university internship regulations.",
        backstory="You apply official internship policies and document any violations.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_supervisor_verification_agent(llm: LLM) -> Agent:
    return Agent(
        role="Supervisor Verification Specialist",
        goal="Draft supervisor verification emails when concerns arise.",
        backstory="You assess company and supervisor details and prepare verification outreach.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


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
