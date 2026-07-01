import json
import os
from datetime import datetime
from pathlib import Path

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

# ── Google Sheets setup ────────────────────────────────────────────────────────

def _get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not creds_json or not sheet_id:
        return None

    info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def _sheet_available() -> bool:
    return bool(os.getenv("GOOGLE_CREDENTIALS_JSON") and os.getenv("GOOGLE_SHEETS_ID"))


# ── Public API (same signatures as before) ────────────────────────────────────

def log_case(
    case_id: str,
    student_email: str,
    pdf_path: str,
    agent_outputs: dict,
    human_decision: dict,
) -> str:
    timestamp = datetime.now().isoformat()
    ai_rec = agent_outputs.get("final_recommendation", "")
    decision = human_decision.get("decision", "PENDING")
    notes = human_decision.get("notes", "")

    if _sheet_available():
        try:
            sheet = _get_sheet()
            sheet.append_row([
                case_id, timestamp, student_email, pdf_path,
                ai_rec, decision, notes, ""
            ])
            print(f"[AUDIT] Case logged to Google Sheets: {case_id}")
            return f"sheets:{case_id}"
        except Exception as e:
            print(f"[AUDIT] Sheets write failed, falling back to JSON: {e}")

    # fallback — JSON
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(LOGS_DIR, f"case_{case_id}_{ts}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "case_id": case_id, "timestamp": timestamp,
            "student_email": student_email, "pdf_path": pdf_path,
            "agent_outputs": agent_outputs, "human_decision": human_decision,
        }, f, indent=2, ensure_ascii=False)
    print(f"[AUDIT] Case log saved: {filepath}")
    return filepath


def update_human_decision(case_id: str, decision: str, notes: str = "") -> bool:
    decided_at = datetime.now().isoformat()

    if _sheet_available():
        try:
            sheet = _get_sheet()
            rows = sheet.get_all_values()
            for i, row in enumerate(rows[1:], start=2):  # skip header
                if row and row[0] == case_id:
                    sheet.update_cell(i, 6, decision)   # F = decision
                    sheet.update_cell(i, 7, notes)       # G = notes
                    sheet.update_cell(i, 8, decided_at)  # H = decided_at
                    return True
            return False
        except Exception as e:
            print(f"[AUDIT] Sheets update failed, falling back to JSON: {e}")

    # fallback — JSON
    os.makedirs(LOGS_DIR, exist_ok=True)
    for f in Path(LOGS_DIR).glob(f"case_{case_id}_*.json"):
        entry = json.loads(f.read_text(encoding="utf-8"))
        entry["human_decision"] = {"decision": decision, "notes": notes}
        entry["human_decision_at"] = decided_at
        f.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    return False


def load_all_cases() -> list:
    if _sheet_available():
        try:
            sheet = _get_sheet()
            rows = sheet.get_all_values()
            if len(rows) <= 1:
                return []
            headers = rows[0]
            cases = []
            for row in rows[1:]:
                # pad short rows
                while len(row) < len(headers):
                    row.append("")
                r = dict(zip(headers, row))
                cases.append({
                    "case_id": r.get("case_id", ""),
                    "timestamp": r.get("timestamp", ""),
                    "student_email": r.get("student_email", ""),
                    "pdf_path": r.get("pdf_path", ""),
                    "agent_outputs": {"final_recommendation": r.get("ai_recommendation", "")},
                    "human_decision": {
                        "decision": r.get("decision", "PENDING"),
                        "notes": r.get("notes", ""),
                    },
                    "human_decision_at": r.get("decided_at", ""),
                })
            return list(reversed(cases))
        except Exception as e:
            print(f"[AUDIT] Sheets read failed, falling back to JSON: {e}")

    # fallback — JSON
    os.makedirs(LOGS_DIR, exist_ok=True)
    cases = []
    for f in sorted(Path(LOGS_DIR).glob("case_*.json"), reverse=True):
        try:
            cases.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return cases


def generate_case_id(student_email: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    prefix = student_email.split("@")[0].upper()[:8]
    return f"{prefix}_{timestamp}"
