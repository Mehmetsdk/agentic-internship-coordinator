import json
import os
from datetime import datetime
from pathlib import Path


LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")


def log_case(
    case_id: str,
    student_email: str,
    pdf_path: str,
    agent_outputs: dict,
    human_decision: dict,
) -> str:
    """
    Saves a full audit log for a processed internship application.
    Returns the path to the log file.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"case_{case_id}_{timestamp}.json"
    filepath = os.path.join(LOGS_DIR, filename)

    log_entry = {
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "student_email": student_email,
        "pdf_path": pdf_path,
        "agent_outputs": agent_outputs,
        "human_decision": human_decision,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    print(f"\n[AUDIT] Case log saved: {filepath}")
    return filepath


def update_human_decision(case_id: str, decision: str, notes: str = "") -> bool:
    """Update the human coordinator's decision for an existing case."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    for f in Path(LOGS_DIR).glob(f"case_{case_id}_*.json"):
        entry = json.loads(f.read_text(encoding="utf-8"))
        entry["human_decision"] = {"decision": decision, "notes": notes}
        entry["human_decision_at"] = datetime.now().isoformat()
        f.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    return False


def load_all_cases() -> list:
    """Load all case logs sorted by timestamp descending."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    cases = []
    for f in sorted(Path(LOGS_DIR).glob("case_*.json"), reverse=True):
        try:
            cases.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return cases


def generate_case_id(student_email: str) -> str:
    """Generates a simple case ID from email and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    prefix = student_email.split("@")[0].upper()[:8]
    return f"{prefix}_{timestamp}"
