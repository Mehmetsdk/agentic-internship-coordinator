"""Standalone test panel for Report Reviewer.

Run with: python3 -m streamlit run report_reviewer/test_panel.py
"""

import streamlit as st
import tempfile
from pathlib import Path
import re

from report_reviewer.intake.classify import classify_submission
from report_reviewer.signing.certificate import generate_certificate
from report_reviewer.checks.rules import run_all_checks

st.set_page_config(page_title="Internship Report Reviewer", page_icon="📋", layout="centered")

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

student_name = st.text_input("Student name", value="Test Student")
student_email = st.text_input("Student email", value="test@ata.edu.tr")
coordinator_name = st.text_input("Coordinator name", value="")

if file_1 and file_2:
    if st.button("Classify"):
        with tempfile.TemporaryDirectory() as tmpdir:
            path_1 = Path(tmpdir) / "file1.pdf"
            path_2 = Path(tmpdir) / "file2.pdf"
            path_1.write_bytes(file_1.getvalue())
            path_2.write_bytes(file_2.getvalue())

            result = classify_submission(str(path_1), str(path_2))
            st.session_state["classification_result"] = result
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

    tabs = st.tabs(["Overview", "Validation", "Learning Outcomes", "Journal"])

    # Overview tab
    with tabs[0]:
        st.markdown('<div style="color:#666;font-size:0.9rem;margin-bottom:0.6rem">Summary of classification and quick verification metrics</div>', unsafe_allow_html=True)

        # Pipeline stripe
        st.markdown("**Pipeline:**  ① Upload  →  ② Extract  →  ③ Compare  →  ④ Decide")

        # File cards (Report / Journal) placed immediately under pipeline
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


        # Classification metadata
        if meta["fully_classified"]:
            st.success("Both documents were classified successfully.")
        else:
            st.warning("Classification is incomplete.")
        for w in meta.get("warnings", []):
            st.warning(w)

        # Metrics (from checks)
        cols = st.columns(3)
        if checks_result:
            with cols[0]:
                st.metric("Passed", checks_result.get("passed_count", 0))
            with cols[1]:
                # support both warning_count and warnings_count keys
                warnings_val = checks_result.get("warning_count", checks_result.get("warnings_count", 0))
                st.metric("Warnings", warnings_val)
            with cols[2]:
                st.metric("Failed", checks_result.get("failed_count", 0))

            status = checks_result.get("overall_status", "UNKNOWN")
            color = "#9ae6b4" if status == "APPROVED" else ("#fef3c7" if status == "REQUEST_CLARIFICATION" else "#fecaca")
            status_label = status.replace("_", " ")
            st.markdown(f'<div style="background:{color};padding:0.8rem;border-radius:8px;margin:0.6rem 0;font-weight:600">Overall status: {status_label}</div>', unsafe_allow_html=True)
        else:
            with cols[0]:
                st.metric("Passed", 0)
            with cols[1]:
                st.metric("Warnings", 0)
            with cols[2]:
                st.metric("Failed", 0)
            st.info("Verification checks not available.")

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

    # Step 3 — Coordinator approval and signing (renumbered)
    st.markdown('<span class="section-label">Step 3 — Coordinator approval and signing</span>', unsafe_allow_html=True)

    if meta["fully_classified"]:
        checks_result = st.session_state.get("checks_result")

        # If checks ran and the overall status is REJECTED, disable signing
        if checks_result and checks_result.get("overall_status") == "REJECTED":
            st.error("Bu başvuru reddedildi, imzalanamaz")
        else:
            # If there are clarification requests, warn the coordinator but allow signing
            if checks_result and checks_result.get("overall_status") == "REQUEST_CLARIFICATION":
                st.warning("Açık noktalar var, onaylamadan önce inceleyin")

            acknowledge = st.checkbox("I have reviewed the documents and approve issuing the certificate")
            if acknowledge and coordinator_name.strip():
                if st.button("Sign & Issue Certificate", type="primary"):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        report_path = Path(tmpdir) / "report.pdf"
                        journal_path = Path(tmpdir) / "journal.pdf"
                        report_path.write_bytes(st.session_state["report_bytes"])
                        journal_path.write_bytes(st.session_state["journal_bytes"])

                        cert_result = generate_certificate(
                            student_name=student_name,
                            student_email=student_email,
                            report_path=str(report_path),
                            journal_path=str(journal_path),
                            coordinator_name=coordinator_name,
                        )

                        st.success("Certificate generated successfully.")

                        st.markdown(f"""
<div style="background:#fff;border:1px solid #e0ddd8;border-radius:10px;padding:1.2rem 1.4rem;font-family:monospace;font-size:0.82rem;line-height:1.8;">
Report hash: {cert_result['report_hash']}<br>
Journal hash: {cert_result['journal_hash']}<br>
Package hash: {cert_result['package_hash']}<br>
Issued at: {cert_result['issued_at']}
</div>
""", unsafe_allow_html=True)

                        cert_bytes = Path(cert_result["certificate_path"]).read_bytes()
                        st.download_button(
                            "Download certificate",
                            cert_bytes,
                            file_name="certificate.pdf",
                            mime="application/pdf",
                        )
            elif not coordinator_name.strip():
                st.info("Enter the coordinator name.")
    else:
        st.error("Signing is disabled because documents were not fully classified.")