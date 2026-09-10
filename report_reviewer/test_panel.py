"""Standalone test panel for Report Reviewer.

Run with: python3 -m streamlit run report_reviewer/test_panel.py
"""

import streamlit as st
import tempfile
from pathlib import Path
import re
import random
import string
import pandas as pd

from report_reviewer.intake.classify import classify_submission
from report_reviewer.signing.certificate import generate_certificate
from report_reviewer.checks.rules import run_all_checks

st.set_page_config(page_title="Internship Report Reviewer", page_icon="📋", layout="wide", initial_sidebar_state="expanded")


def render_sidebar_queue():
    """Render the left fixed Queue sidebar with simple cards."""
    with st.sidebar:
        st.markdown("### Queue")
        st.caption("To sign / With student / Signed")

        # simple badges for counts based on session state
        pending = 1 if st.session_state.get("classification_result") else 0
        with_student = 0
        signed = 1 if st.session_state.get("last_certificate") else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("To sign", pending)
        c2.metric("With student", with_student)
        c3.metric("Signed", signed)

        st.markdown("---")

        # Show a small list of application cards (derive from current classification if available)
        if st.session_state.get("classification_result"):
            res = st.session_state["classification_result"]
            meta = res.get("submission_metadata", {})
            # prefer student name from form/session state
            student = st.session_state.get("student_name") or meta.get("student_name") or "Unknown Student"
            # classify.py does not currently populate employer/duration; keep safe defaults
            company = meta.get("employer") or meta.get("company") or "Unknown Employer"
            checks_result = st.session_state.get("checks_result") or {}
            status = checks_result.get("overall_status", "PENDING")
            days = meta.get("duration_days", "N/A")

            st.markdown(f"**{student}**")
            st.markdown(f"{company} • {status} • {days} days")
            st.markdown("\n")
        else:
            st.info("No submissions in queue")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'DM Sans', -apple-system, sans-serif; }
.stApp { background: #f7f6f3; }
.block-container { padding: 2.5rem 3rem !important; max-width: 900px !important; }

.header-box {
    background: #fff;
    border: 1px solid #e0ddd8;
    border-radius: 16px;
    padding: 2rem 2.4rem;
    margin-bottom: 2rem;
}
.header-title {
    font-family: Georgia, serif;
    font-size: 2.2rem;
    color: #1a1a1a;
    margin-bottom: 0.4rem;
}
.header-sub {
    font-size: 0.95rem;
    color: #777;
}
.section-label {
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #999;
    margin: 1.6rem 0 0.6rem 0;
    display: block;
}

.stButton>button {
    border-radius: 8px !important;
    border: 1px solid #e0ddd8 !important;
    background: #fff !important;
    color: #1a1a1a !important;
}
.stButton>button:hover {
    background: #f26b1d !important;
    color: #fff !important;
    border-color: #f26b1d !important;
}
button[kind="primary"] {
    background: #f26b1d !important;
    color: #fff !important;
    border: none !important;
}
button[kind="primary"]:hover {
    background: #d95f18 !important;
}

[data-testid="stFileUploader"], .stTextInput>div>div>input {
    border-radius: 8px !important;
}

#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;color:#f26b1d;font-weight:600;margin-bottom:0.5rem;">Academic Workflow Automation</div>
    <div class="header-title">Internship Report Reviewer</div>
    <div class="header-sub">Test panel for report and journal verification</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<span class="section-label">Step 1 — Upload documents</span>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    file_1 = st.file_uploader("First PDF", type="pdf", key="file1")
with col2:
    file_2 = st.file_uploader("Second PDF", type="pdf", key="file2")

student_name = st.text_input("Student name", value="Test Student", key="student_name")
student_email = st.text_input("Student email", value="test@ata.edu.tr")
coordinator_name = st.text_input("Coordinator name", value="")


# --- New render helper functions for Pomelo-like layout
def render_header():
    """Top header with project icon, search and awaiting signature counter."""
    with st.container():
        hcol1, hcol2, hcol3 = st.columns([1, 3, 1])
        with hcol1:
            st.markdown("<div style='font-size:1.1rem;font-weight:700'>📋 Report Reviewer</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:0.8rem;color:#777'>Internship completions</div>", unsafe_allow_html=True)
        with hcol2:
            st.text_input("", key="search_box", placeholder="Search student, company or ID")
        with hcol3:
            awaiting = 1 if st.session_state.get("classification_result") and not st.session_state.get("last_certificate") else 0
            st.markdown(f"<div style='text-align:right'><span style='font-weight:600'>{awaiting} awaiting signature</span><div style='color:#777;font-size:0.8rem'>updated just now</div></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:right;margin-top:6px'><button style='background:#f26b1d;color:#fff;border:none;padding:6px 10px;border-radius:6px'>+ Submit</button></div>", unsafe_allow_html=True)


def render_metrics(checks_result, report_wc, entries_val, hours_val):
    """Render four metric cards with progress bars and thresholds."""
    thresh_days = 20
    working_days = entries_val if isinstance(entries_val, int) else 0
    pct_days = min(1.0, working_days / thresh_days) if thresh_days else 0

    # Employer score and peak similarity may not be available; show N/A
    emp_score = None
    peak_sim = None

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    # WORKING DAYS
    with mcol1:
        st.markdown("**WORKING DAYS**")
        st.markdown(f"<div style='font-size:22px;font-weight:700'>{working_days}</div>", unsafe_allow_html=True)
        st.progress(pct_days)
        st.caption(f"{thresh_days} to pass")

    # NAME MATCH (from NAME_CONSISTENCY check)
    name_status = 'N/A'
    lo_status = 'N/A'
    if checks_result:
        for c in checks_result.get('checks', []):
            code = (c.get('code') or '').upper()
            if code == 'NAME_CONSISTENCY':
                name_status = c.get('status', 'N/A')
            if code in ('REQUIRED_CONTENT', 'LEARNING_OUTCOME'):
                lo_status = c.get('status', 'N/A')

    def status_pct(s):
        return 1.0 if str(s).upper() == 'PASS' else (0.5 if str(s).upper() == 'WARNING' else 0.0)

    with mcol2:
        st.markdown("**NAME MATCH**")
        st.markdown(f"<div style='font-size:22px;font-weight:700'>{name_status}</div>", unsafe_allow_html=True)
        st.progress(status_pct(name_status))
        st.caption("Student name consistency")

    # REPORT LENGTH
    with mcol3:
        st.markdown("**REPORT LENGTH**")
        st.markdown(f"<div style='font-size:22px;font-weight:700'>{report_wc}</div>", unsafe_allow_html=True)
        # assume 2000 words target
        st.progress(min(1.0, report_wc / 2000 if report_wc else 0))
        st.caption("2000 to pass")

    # LEARNING OUTCOME (from REQUIRED_CONTENT)
    with mcol4:
        st.markdown("**LEARNING OUTCOME**")
        st.markdown(f"<div style='font-size:22px;font-weight:700'>{lo_status}</div>", unsafe_allow_html=True)
        st.progress(status_pct(lo_status))
        st.caption("Expected learning outcome language")


def render_findings(checks_result):
    """Show a one-line findings summary and green banner if all passed."""
    if not checks_result:
        st.info("No automated checks run yet.")
        return
    overall = checks_result.get("overall_status", "UNKNOWN")
    if overall == "APPROVED":
        st.success("Every automated check passed — ready to issue certificate.")
    elif overall == "REQUEST_CLARIFICATION":
        st.warning("Some checks raised warnings — review findings and request clarification.")
    else:
        st.error("One or more checks failed — submission rejected.")


def render_certificate_panel(student_name, student_email, coordinator_name, report_bytes, journal_bytes, checks_result):
    """Right-side fixed certificate panel with inputs and sign action."""
    st.markdown("""
    <div style='background:#fff;border:1px solid #e0ddd8;border-radius:12px;padding:12px;'>
    """, unsafe_allow_html=True)
    st.markdown("**CERTIFICATE**")
    cname = st.text_input("Your name", value=coordinator_name, key="cert_coordinator")
    note = st.text_area("Note (optional)", key="cert_note")
    signature = st.text_input("Signature (type initials)", key="cert_signature")

    ccol1, ccol2 = st.columns([1, 1])
    with ccol1:
        if st.button("Clear", key="cert_clear"):
            st.session_state["cert_coordinator"] = ""
            st.session_state["cert_note"] = ""
            st.session_state["cert_signature"] = ""
            st.info("Cleared certificate inputs")
    with ccol2:
        if st.button("Sign certificate", key="sign_cert_button"):
            if not cname:
                st.error("Enter your name to sign.")
            elif checks_result and checks_result.get("overall_status") == "REJECTED":
                st.error("Cannot sign: submission rejected by automated checks.")
            else:
                if not report_bytes or not journal_bytes:
                    st.error("Missing document bytes; run classification first.")
                else:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        report_path = Path(tmpdir) / "report.pdf"
                        journal_path = Path(tmpdir) / "journal.pdf"
                        report_path.write_bytes(report_bytes)
                        journal_path.write_bytes(journal_bytes)

                        cert_result = generate_certificate(
                            student_name=student_name,
                            student_email=student_email,
                            report_path=str(report_path),
                            journal_path=str(journal_path),
                            coordinator_name=cname,
                        )

                        st.success("Certificate generated successfully.")
                        st.markdown(f"**Issued at:** {cert_result['issued_at']}")
                        st.download_button("Download certificate", Path(cert_result['certificate_path']).read_bytes(), file_name="certificate.pdf", mime="application/pdf")

    st.markdown("</div>", unsafe_allow_html=True)

if file_1 and file_2:
    if st.button("Classify"):
        with tempfile.TemporaryDirectory() as tmpdir:
            path_1 = Path(tmpdir) / "file1.pdf"
            path_2 = Path(tmpdir) / "file2.pdf"
            path_1.write_bytes(file_1.getvalue())
            path_2.write_bytes(file_2.getvalue())

            result = classify_submission(str(path_1), str(path_2))
            st.session_state["classification_result"] = result
            # generate a submission reference for this classification
            ref = "SUB-" + "".join(random.choices(string.digits, k=7))
            st.session_state["submission_ref"] = ref
            # store bytes for later signing
            st.session_state["report_bytes"] = (
                file_1.getvalue() if result["report_file"] == str(path_1) else file_2.getvalue()
            )
            st.session_state["journal_bytes"] = (
                file_2.getvalue() if result["journal_file"] == str(path_2) else file_1.getvalue()
            )
            # store original uploaded filenames so we can display mapping later
            st.session_state["file1_name"] = getattr(file_1, "name", None)
            st.session_state["file2_name"] = getattr(file_2, "name", None)
            st.session_state["report_filename"] = (
                file_1.name if result["report_file"] == str(path_1) else file_2.name
            )
            st.session_state["journal_filename"] = (
                file_2.name if result["journal_file"] == str(path_2) else file_1.name
            )

if "classification_result" in st.session_state:
    result = st.session_state["classification_result"]
    # Combined Classification + Verification UI (tabbed)
    meta = result["submission_metadata"]

    # Run checks and store in session state (preserve functional behavior)
    try:
        checks_result = run_all_checks(result.get("report_text", ""), result.get("journal_text", ""), student_name)
    except Exception as e:
        st.error(f"Error running verification checks: {e}")
        checks_result = None

    st.session_state["checks_result"] = checks_result

    # Prepare filenames
    report_filename = st.session_state.get("report_filename")
    journal_filename = st.session_state.get("journal_filename")

    # Render top header
    render_header()
    # Render sidebar queue here so it sees updated classification/checks
    render_sidebar_queue()

    # Main layout: center details + right certificate panel
    main_col, right_col = st.columns([3, 1])
    with main_col:
        tabs = st.tabs(["Overview", "Validation", "Learning Outcomes", "Journal", "Extracted Data"])

        # Overview tab (compact, now inside main column)
        with tabs[0]:
            st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Summary of classification and quick verification metrics</div>', unsafe_allow_html=True)
            st.markdown("**Pipeline:**  ① Upload  →  ② Extract  →  ③ Compare  →  ④ Decide")

            r_filename = report_filename or "Unknown"
            j_filename = journal_filename or "Unknown"
            report_text = result.get("report_text", "") or ""
            journal_text = result.get("journal_text", "") or ""
            report_word_count = len(report_text.split()) if report_text else 0
            journal_word_count = len(journal_text.split()) if journal_text else 0

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e0ddd8;border-radius:12px;padding:1.2rem 1.4rem;">
                    <div style="font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#999;margin-bottom:0.4rem;">REPORT</div>
                    <div style="font-weight:600;font-size:1rem;color:#1a1a1a;margin-bottom:0.3rem;">{r_filename}</div>
                    <div style="font-size:0.82rem;color:#777;">{report_word_count} words</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e0ddd8;border-radius:12px;padding:1.2rem 1.4rem;">
                    <div style="font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#999;margin-bottom:0.4rem;">JOURNAL</div>
                    <div style="font-weight:600;font-size:1rem;color:#1a1a1a;margin-bottom:0.3rem;">{j_filename}</div>
                    <div style="font-size:0.82rem;color:#777;">{journal_word_count} words</div>
                </div>
                """, unsafe_allow_html=True)

            if meta["fully_classified"]:
                st.success("Both documents were classified successfully.")
                if st.session_state.get("submission_ref"):
                    st.caption(f"Reference: {st.session_state.get('submission_ref')}")
            else:
                st.warning("Classification is incomplete.")
            for w in meta.get("warnings", []):
                st.warning(w)

            # derive entries/hours for metrics
            entries_val = 0
            hours_val = 0
            if checks_result:
                for c in checks_result.get("checks", []):
                    code = c.get("code") or c.get("id") or c.get("name")
                    if code and str(code).upper() == "JOURNAL_HOURS":
                        msg = c.get("message", "")
                        m = re.search(r"(\d+) journal entries found, estimated ([\d.]+) total hours", msg)
                        if m:
                            entries_val = int(m.group(1))
                            hours_val = float(m.group(2))

            render_findings(checks_result)
            render_metrics(checks_result, report_word_count, entries_val, hours_val)

    # Validation tab: list each check
    with tabs[1]:
        st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Detailed list of validation checks and their outcomes</div>', unsafe_allow_html=True)
        if checks_result and checks_result.get("checks"):
            for c in checks_result.get("checks", []):
                c_status = str(c.get("status", "")).upper()
                message = c.get("message", "")
                if c_status in ("PASS", "PASSED", "OK"):
                    st.success(message)
                elif c_status in ("WARNING", "WARN"):
                    st.warning(message)
                else:
                    st.error(message)
        else:
            st.info("No validation checks available.")

    # Learning Outcomes tab: report text + counts
    with tabs[2]:
        st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Extracted learning outcomes from the classified report</div>', unsafe_allow_html=True)
        report_text = result.get("report_text", "") or ""
        word_count = len(report_text.split()) if report_text else 0
        char_count = len(report_text)

        # metrics: Words / Characters / Classification
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Words", word_count)
        with mcol2:
            st.metric("Characters", char_count)
        with mcol3:
            st.metric("Classification", "Report")

        st.divider()

        if report_text:
            st.text_area("Report text", report_text, height=300, key="report_full_text")
        else:
            st.info("No report text available.")

    # Journal tab: journal text + entries info
    with tabs[3]:
        st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Extracted journal content and entry metrics</div>', unsafe_allow_html=True)
        journal_text = result.get("journal_text", "") or ""

        # Extract entries and estimated hours from JOURNAL_HOURS check message
        entries_val = "N/A"
        hours_val = "N/A"
        if checks_result:
            for c in checks_result.get("checks", []):
                code = c.get("code") or c.get("id") or c.get("name")
                if code and str(code).upper() == "JOURNAL_HOURS":
                    message = c.get("message", "")
                    match = re.search(r"(\d+) journal entries found, estimated ([\d.]+) total hours", message)
                    if match:
                        entries_val = int(match.group(1))
                        hours_val = float(match.group(2))
                    else:
                        # try to extract numbers more loosely
                        m2 = re.search(r"(\d+) journal entries", message)
                        m3 = re.search(r"([\d.]+) total hours", message)
                        if m2:
                            entries_val = int(m2.group(1))
                        if m3:
                            hours_val = float(m3.group(1))
                    break

        # show metrics: Entries / Estimated Hours / Classification
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Entries", entries_val)
        with mcol2:
            st.metric("Estimated Hours", hours_val)
        with mcol3:
            st.metric("Classification", "Journal")

        st.divider()

        if journal_text:
            st.text_area("Journal text", journal_text, height=300, key="journal_full_text")
        else:
            st.info("No journal text available.")

    # Extracted Data tab: show raw extracted values
    with tabs[4]:
        st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Raw values extracted from the documents during validation</div>', unsafe_allow_html=True)

        if not checks_result:
            st.info("Run classification first.")
        else:
            # Student name (input)
            student_input = student_name

            # Journal date range from DATE_CONSISTENCY check
            date_range_str = "N/A"
            entries_val = "N/A"
            hours_val = "N/A"
            for c in checks_result.get("checks", []):
                code = c.get("code") or c.get("id") or c.get("name")
                if code and str(code).upper() == "DATE_CONSISTENCY":
                    msg = c.get("message", "")
                    m = re.search(r"from ([\d.]+) to ([\d.]+)", msg)
                    if m:
                        date_range_str = f"{m.group(1)} to {m.group(2)}"
                if code and str(code).upper() == "JOURNAL_HOURS":
                    msg = c.get("message", "")
                    m = re.search(r"(\d+) journal entries found, estimated ([\d.]+) total hours", msg)
                    if m:
                        entries_val = int(m.group(1))
                        hours_val = float(m.group(2))
                    else:
                        m2 = re.search(r"(\d+) journal entries", msg)
                        m3 = re.search(r"([\d.]+) total hours", msg)
                        if m2:
                            entries_val = int(m2.group(1))
                        if m3:
                            hours_val = float(m3.group(1))

            report_wc = len(result.get("report_text", "").split()) if result.get("report_text") else 0
            journal_wc = len(result.get("journal_text", "").split()) if result.get("journal_text") else 0

            extracted_data = {
                "Field": [
                    "Student name (input)",
                    "Journal date range",
                    "Journal entries",
                    "Estimated hours",
                    "Report word count",
                    "Journal word count",
                ],
                "Value": [
                    str(student_input),
                    str(date_range_str),
                    str(entries_val),
                    str(hours_val),
                    str(report_wc),
                    str(journal_wc),
                ],
            }

            df = pd.DataFrame(extracted_data)
            st.table(df)

    # Right column: certificate panel
    with right_col:
        render_certificate_panel(
            student_name=student_name,
            student_email=student_email,
            coordinator_name=coordinator_name,
            report_bytes=st.session_state.get("report_bytes"),
            journal_bytes=st.session_state.get("journal_bytes"),
            checks_result=checks_result,
        )