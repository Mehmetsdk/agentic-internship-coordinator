# Groq cache_breakpoint uyumsuzluğunu düzelt (CrewAI 1.14+ bug)
import crewai.llms.cache as _cache_mod
_cache_mod.mark_cache_breakpoint = lambda msg: msg  # noqa: E731

from dotenv import load_dotenv
from crewai import Crew, Process, Task, LLM
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

from human_review import get_human_decision
from audit_logger import log_case, generate_case_id
from agents import (
    create_email_intake_agent,
    create_document_extraction_agent,
    create_completeness_validation_agent,
    create_university_rules_agent,
    create_supervisor_verification_agent,
    create_decision_recommendation_agent,
)

load_dotenv()

import os

groq_llm = LLM(
    model="anthropic/claude-haiku-4-5-20251001",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

langfuse_client = Langfuse()

TASK_NAMES = [
    "email_intake",
    "document_extraction",
    "completeness_check",
    "university_rules",
    "supervisor_verification",
    "decision_recommendation",
]


@observe()
def run_pipeline(pdf_path: str, student_email: str) -> dict:
    case_id = generate_case_id(student_email)
    email_intake = create_email_intake_agent(groq_llm)
    doc_extraction = create_document_extraction_agent(groq_llm)
    completeness = create_completeness_validation_agent(groq_llm)
    rules = create_university_rules_agent(groq_llm)
    supervisor = create_supervisor_verification_agent(groq_llm)
    decision = create_decision_recommendation_agent(groq_llm)

    task_intake = Task(
        description=f"Process the internship application received from {student_email}. The PDF is located at: {pdf_path}",
        expected_output="Confirmation that the application email was received and the PDF path is ready for extraction.",
        agent=email_intake,
    )

    task_extraction = Task(
        description=f"Extract all student and company data from the PDF at {pdf_path}.",
        expected_output="A structured summary of: student name, student ID, field of study, semester, company name, supervisor name, supervisor email, internship dates.",
        agent=doc_extraction,
    )

    task_completeness = Task(
        description="Check the extracted data for missing or incomplete fields.",
        expected_output="A completeness report listing which fields are present and which are missing or unclear.",
        agent=completeness,
    )

    task_rules = Task(
        description="Validate the application against university internship regulations.",
        expected_output="A compliance report stating whether the application passes all rules, and listing any violations.",
        agent=rules,
    )

    task_supervisor = Task(
        description="If there are any concerns about the company or supervisor, draft a verification email to the supervisor.",
        expected_output="Either 'No verification needed' or a draft verification email ready to be sent.",
        agent=supervisor,
    )

    task_decision = Task(
        description="Based on all previous results, produce a final recommendation for the human coordinator.",
        expected_output="A recommendation of APPROVE / REJECT / REQUEST CLARIFICATION with a concise justification.",
        agent=decision,
    )

    crew = Crew(
        agents=[email_intake, doc_extraction, completeness, rules, supervisor, decision],
        tasks=[task_intake, task_extraction, task_completeness, task_rules, task_supervisor, task_decision],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    ai_recommendation = str(result)

    # Log each agent task as a child span
    trace_id = langfuse_context.get_current_trace_id()
    for i, task in enumerate(crew.tasks):
        if task.output:
            output_text = task.output.raw if hasattr(task.output, "raw") else str(task.output)
            span = langfuse_client.span(
                trace_id=trace_id,
                name=TASK_NAMES[i],
                input=task.description,
                output=output_text,
            )
            span.end()

    # Update trace output with meaningful info
    langfuse_context.update_current_observation(
        output={"ai_recommendation": ai_recommendation, "case_id": case_id},
        metadata={"student_email": student_email},
    )

    # Save with PENDING status — coordinator decides via dashboard
    log_case(
        case_id=case_id,
        student_email=student_email,
        pdf_path=pdf_path,
        agent_outputs={"final_recommendation": ai_recommendation},
        human_decision={"decision": "PENDING", "notes": ""},
    )

    return {"decision": "PENDING", "notes": ai_recommendation, "case_id": case_id}


if __name__ == "__main__":
    final = run_pipeline(
        pdf_path="data/test_applications/sample.pdf",
        student_email="student@example.com",
    )
    print(f"\nFinal coordinator decision: {final['decision']}")
    if final["notes"]:
        print(f"Notes: {final['notes']}")
