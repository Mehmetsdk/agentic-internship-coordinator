"""Independent test panel for Report Reviewer.

Run with: streamlit run report_reviewer/test_panel.py

This panel is INDEPENDENT from the main dashboard.py and is intended to test
all steps (classification + certificate generation) until the flow is ready.
"""

import streamlit as st
import tempfile
from pathlib import Path

from report_reviewer.intake.classify import classify_submission
from report_reviewer.signing.certificate import generate_certificate

st.set_page_config(page_title="Report Reviewer - Test Panel", page_icon="📋")

st.title("📋 Internship Report Reviewer — Test Panel")
st.caption("Independent testing tool - to be integrated into the main dashboard")

st.divider()

st.subheader("1. Upload documents")
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
    st.divider()
    st.subheader("2. Classification result")

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
            st.text_area("Text (first 500 characters)", result["report_text"][:500], height=150, key="report_preview")
        else:
            st.info("Not found")
    with col2:
        st.markdown("**Journal**")
        if result["journal_text"]:
            st.text_area("Text (first 500 characters)", result["journal_text"][:500], height=150, key="journal_preview")
        else:
            st.info("Not found")

    st.divider()
    st.subheader("3. Coordinator approval and signing")

    if meta["fully_classified"]:
        acknowledge = st.checkbox("I reviewed the documents and approve certificate generation")
        if acknowledge and coordinator_name.strip():
            if st.button("🖊 Sign & Issue Certificate", type="primary"):
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

                    st.success("Certificate generated successfully!")
                    st.json(cert_result)

                    cert_bytes = Path(cert_result["certificate_path"]).read_bytes()
                    st.download_button(
                        "📄 Download certificate",
                        cert_bytes,
                        file_name="certificate.pdf",
                        mime="application/pdf",
                    )
        elif not coordinator_name.strip():
            st.info("Please enter the coordinator name.")
    else:
        st.error("Signing is disabled because the documents were not fully classified.")
