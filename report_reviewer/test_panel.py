"""Standalone test panel for Report Reviewer.

Run with: python3 -m streamlit run report_reviewer/test_panel.py
"""

import streamlit as st
import tempfile
from pathlib import Path

from report_reviewer.intake.classify import classify_submission
from report_reviewer.signing.certificate import generate_certificate

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
            st.session_state["report_bytes"] = (
                file_1.getvalue() if result["report_file"] == str(path_1) else file_2.getvalue()
            )
            st.session_state["journal_bytes"] = (
                file_2.getvalue() if result["journal_file"] == str(path_2) else file_1.getvalue()
            )

if "classification_result" in st.session_state:
    result = st.session_state["classification_result"]
    st.markdown('<span class="section-label">Step 2 — Classification result</span>', unsafe_allow_html=True)

    meta = result["submission_metadata"]
    if meta["fully_classified"]:
        st.success("Both documents were classified successfully.")
    else:
        st.warning("Classification is incomplete.")

    for w in meta["warnings"]:
        st.warning(w)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Report (learning outcomes)**")
        if result["report_text"]:
            st.text_area("Preview", result["report_text"][:500], height=150, key="report_preview")
        else:
            st.info("Not found")
    with col2:
        st.markdown("**Journal**")
        if result["journal_text"]:
            st.text_area("Preview", result["journal_text"][:500], height=150, key="journal_preview")
        else:
            st.info("Not found")

    st.markdown('<span class="section-label">Step 3 — Coordinator approval and signing</span>', unsafe_allow_html=True)

    if meta["fully_classified"]:
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