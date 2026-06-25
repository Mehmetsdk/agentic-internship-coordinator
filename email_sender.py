import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
load_dotenv()

DECISION_SUBJECTS = {
    "APPROVE": "Your Internship Application Has Been Approved",
    "REJECT":  "Update on Your Internship Application",
    "CLARIFY": "Clarification Required — Internship Application",
}

DECISION_BODIES = {
    "APPROVE": (
        "Congratulations! Your internship application has been reviewed and "
        "approved by the coordinator.\n\n"
        "You will be contacted with the next steps shortly."
    ),
    "REJECT": (
        "Thank you for submitting your internship application. After careful review, "
        "we regret to inform you that your application was not approved at this time.\n\n"
        "If you have questions or would like feedback, please contact the internship office."
    ),
    "CLARIFY": (
        "Your internship application requires additional clarification before it can be processed.\n\n"
        "Please resubmit your application with a valid, complete PDF containing all required fields:\n"
        "  1. Student Name\n  2. Student ID\n  3. Field of Study\n  4. Semester\n"
        "  5. Company Name\n  6. Supervisor Name\n  7. Supervisor Email\n  8. Internship Dates"
    ),
}


def send_decision_email(to_email: str, case_id: str, decision: str, notes: str = "") -> tuple[bool, str]:
    """Send a decision notification email. Returns (success, error_message)."""
    sender = os.getenv("SENDER_EMAIL", "").strip()
    password = os.getenv("SENDER_APP_PASSWORD", "").strip().replace(" ", "").replace("-", "")

    if not sender or not password:
        return False, "SENDER_EMAIL or SENDER_APP_PASSWORD not set in .env"

    subject = DECISION_SUBJECTS.get(decision, "Internship Application Update")
    body_intro = DECISION_BODIES.get(decision, "Your application has been reviewed.")

    body = f"""Dear Student,

Your internship application has been reviewed.

Case ID : {case_id}
Decision: {decision}
{f"Notes   : {notes}" if notes and notes.strip() else ""}

{body_intro}

Best regards,
ATA Builders Lab — Internship Coordinator
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)
