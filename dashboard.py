import html as _html
import os
import streamlit as st
from audit_logger import load_all_cases, update_human_decision
from email_sender import send_decision_email

st.set_page_config(page_title="Internship Coordinator", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #f7f6f3; color: #1a1a1a; }
.stApp { background: #f7f6f3; }
.block-container { padding: 2.5rem 3rem !important; max-width: 1300px !important; }
section[data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #e8e5e0 !important; }
.badge { display:inline-block; padding:2px 9px; border-radius:20px; font-size:0.7rem; font-weight:500; }
.badge-PENDING  { background:#fef9e7; color:#b7860c; border:1px solid #f5e49a; }
.badge-APPROVE  { background:#edfaf3; color:#1a7a45; border:1px solid #a8e6c0; }
.badge-REJECT   { background:#fef0f0; color:#c0392b; border:1px solid #f5b7b1; }
.badge-CLARIFY  { background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; }
.detail-section { background:#fff; border:1px solid #e8e5e0; border-radius:8px; padding:1.2rem 1.4rem; margin-bottom:1rem; }
.rec-box { background:#ffffff; border:1px solid #e0ddd8; border-radius:8px; padding:1.2rem 1.4rem; margin-bottom:1rem; font-size:0.88rem; white-space:pre-wrap; color:#1a1a1a !important; line-height:1.75; box-shadow:0 1px 3px rgba(0,0,0,0.06); }
.stButton>button { font-family:'DM Sans',sans-serif !important; border-radius:6px !important; border:1px solid #e0ddd8 !important; background:#fff !important; color:#1a1a1a !important; width:100% !important; }
.stButton>button:hover { background:#1a1a1a !important; color:#fff !important; border-color:#1a1a1a !important; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

cases = load_all_cases()

with st.sidebar:
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Filter</span>', unsafe_allow_html=True)
    status_filter = st.selectbox("Status", ["All", "PENDING", "APPROVE", "REJECT", "CLARIFY"], label_visibility="collapsed")
    st.divider()
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Overview</span>', unsafe_allow_html=True)
    for label, val, color in [
        ("Total", len(cases), "#1a1a1a"),
        ("Pending", sum(1 for c in cases if c.get("human_decision", {}).get("decision") == "PENDING"), "#b7860c"),
        ("Approved", sum(1 for c in cases if c.get("human_decision", {}).get("decision") == "APPROVE"), "#1a7a45"),
        ("Rejected", sum(1 for c in cases if c.get("human_decision", {}).get("decision") == "REJECT"), "#c0392b"),
    ]:
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #f0ede8;"><span style="font-size:0.82rem;color:#666;">{label}</span><span style="font-size:1.1rem;font-weight:600;color:{color};">{val}</span></div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown('<div style="margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid #e0ddd8;"><div style="font-family:Georgia,serif;font-size:2.4rem;color:#1a1a1a;letter-spacing:-0.02em;">Internship <em style="color:#6b6b6b;">Coordinator</em></div><div style="font-size:0.75rem;color:#777;letter-spacing:0.12em;text-transform:uppercase;margin-top:0.4rem;">ATA Builders Lab · Agentic System · CrewAI</div></div>', unsafe_allow_html=True)

if status_filter != "All":
    filtered = [c for c in cases if c.get("human_decision", {}).get("decision") == status_filter]
else:
    filtered = cases

col_list, col_detail = st.columns([2, 3], gap="large")

with col_list:
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Applications</span>', unsafe_allow_html=True)
    if not filtered:
        st.markdown('<div style="color:#999;font-size:0.85rem;padding:1rem 0;">No applications found.</div>', unsafe_allow_html=True)
    for idx, c in enumerate(filtered):
        case_id = c.get("case_id", "?")
        email = c.get("student_email", "?")
        status = c.get("human_decision", {}).get("decision", "PENDING")
        ts = c.get("timestamp", "")[:10]
        bc = f"badge-{status}"
        st.markdown(f'<div style="background:#fff;border:1px solid #e8e5e0;border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="font-size:0.95rem;font-weight:500;color:#1a1a1a;">{email}</div><div style="font-size:0.75rem;color:#777;">{ts}</div></div><span class="badge {bc}">{status}</span></div><div style="font-size:0.68rem;color:#999;margin-top:0.4rem;">{case_id}</div></div>', unsafe_allow_html=True)
        if st.button("Open", key=f"btn_{idx}_{case_id}"):
            st.session_state.selected_id = case_id
            st.rerun()

with col_detail:
    if st.session_state.selected_id:
        case = next((c for c in cases if c.get("case_id") == st.session_state.selected_id), None)
        if case:
            status = case.get("human_decision", {}).get("decision", "PENDING")
            rec = case.get("agent_outputs", {}).get("final_recommendation", "")
            email = case.get("student_email", "—")
            date = case.get("timestamp", "")[:10] or "—"

            st.caption(f"{case['case_id']} · Application Detail")

            field_style = "background:#f7f6f3;border:1px solid #e0ddd8;border-radius:6px;padding:0.5rem 0.8rem;font-size:0.88rem;color:#1a1a1a;font-family:monospace;"
            label_style = "font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#555;margin-bottom:0.4rem;display:block;"
            submitted_at = case.get("timestamp", "")
            try:
                from datetime import datetime as _dt
                submitted_display = _dt.fromisoformat(submitted_at).strftime("%d %b %Y, %H:%M") if submitted_at else "—"
            except Exception:
                submitted_display = submitted_at[:16].replace("T", " ") if submitted_at else "—"
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<span style="{label_style}">Student Email</span><div style="{field_style}">{_html.escape(email)}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<span style="{label_style}">Submitted</span><div style="{field_style}">{_html.escape(submitted_display)}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<span style="{label_style}">Status</span><div style="{field_style}">{_html.escape(status)}</div>', unsafe_allow_html=True)
            st.divider()

            # PDF Viewer
            pdf_path = case.get("pdf_path", "")
            st.markdown(f'<span style="{label_style}">Application PDF</span>', unsafe_allow_html=True)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                import base64
                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="500px" style="border:1px solid #e0ddd8;border-radius:8px;"></iframe>',
                    unsafe_allow_html=True,
                )
                st.download_button("Download PDF", pdf_bytes, file_name=f"{case['case_id']}.pdf", mime="application/pdf")
            else:
                st.markdown(
                    '<div style="background:#fef9f0;border:1px solid #f5e49a;border-radius:8px;padding:0.8rem 1rem;font-size:0.85rem;color:#b7860c;">PDF dosyası bulunamadı — yeniden gönderim gerekebilir.</div>',
                    unsafe_allow_html=True,
                )

            st.divider()

            st.markdown(f'<span style="{label_style}">AI Recommendation</span>', unsafe_allow_html=True)
            rec_safe = _html.escape(rec) if rec else "No recommendation available."
            st.markdown(f'<div style="background:#ffffff;border:1px solid #e0ddd8;border-radius:8px;padding:1.4rem 1.6rem;font-size:0.88rem;color:#1a1a1a;white-space:pre-wrap;line-height:1.75;box-shadow:0 1px 4px rgba(0,0,0,0.06);max-height:400px;overflow-y:auto;">{rec_safe}</div>', unsafe_allow_html=True)

            if status == "PENDING":
                st.markdown('<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;display:block;margin-bottom:0.5rem;">Coordinator Decision</span>', unsafe_allow_html=True)
                notes = st.text_area("Notes (optional)", key="notes_input", label_visibility="collapsed", placeholder="Add notes here...")
                b1, b2, b3 = st.columns(3)
                def _decide(decision, label):
                    update_human_decision(case["case_id"], decision, notes)
                    sem = case.get("student_email", "")
                    if sem and sem != "unknown@unknown.com":
                        ok, err = send_decision_email(sem, case["case_id"], decision, notes)
                        if ok:
                            st.toast(f"Email sent to {sem}", icon="✉")
                        else:
                            st.warning(f"Decision saved but email failed: {err}")

                with b1:
                    if st.button("✓ Approve", key="approve"):
                        _decide("APPROVE", "Approved")
                        st.rerun()
                with b2:
                    if st.button("✕ Decline", key="reject"):
                        _decide("REJECT", "Declined")
                        st.rerun()
                with b3:
                    if st.button("↩ More Info", key="clarify"):
                        _decide("CLARIFY", "More Info")
                        st.rerun()
            else:
                decision_notes = case.get("human_decision", {}).get("notes", "") or ""
                color_map = {"APPROVE": "#1a7a45", "REJECT": "#c0392b", "CLARIFY": "#3730a3"}
                dc = color_map.get(status, "#555")
                st.markdown(
                    f'<div style="background:#fff;border:1px solid #e0ddd8;border-radius:8px;'
                    f'padding:1rem 1.2rem;color:#1a1a1a;font-size:0.9rem;">'
                    f'<span style="font-weight:600;color:{dc};">Decision: {status}</span>'
                    f'{"<br><span style=\\'color:#555;\\'>Notes: " + _html.escape(decision_notes) + "</span>" if decision_notes else ""}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
                student_email_val = case.get("student_email", "")
                if student_email_val and student_email_val != "unknown@unknown.com":
                    if st.button("✉ Send Decision Email", key="send_email", use_container_width=True):
                        ok, err = send_decision_email(
                            to_email=student_email_val,
                            case_id=case["case_id"],
                            decision=status,
                            notes=decision_notes,
                        )
                        if ok:
                            st.success(f"Email sent to {student_email_val}")
                        else:
                            st.error(f"Failed to send email: {err}")
                else:
                    st.warning("Cannot send email — student email is unknown.")
    else:
        st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:300px;color:#ccc;font-size:0.9rem;">Select an application to view details</div>', unsafe_allow_html=True)
