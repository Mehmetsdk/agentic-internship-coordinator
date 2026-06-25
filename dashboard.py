import streamlit as st
from audit_logger import load_all_cases, update_human_decision

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
.rec-box { background:#fff8e7; border:1px solid #f5e49a; border-radius:8px; padding:1rem 1.2rem; margin-bottom:1rem; font-size:0.85rem; white-space:pre-wrap; }
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
    for c in filtered:
        case_id = c.get("case_id", "?")
        email = c.get("student_email", "?")
        status = c.get("human_decision", {}).get("decision", "PENDING")
        ts = c.get("timestamp", "")[:10]
        bc = f"badge-{status}"
        st.markdown(f'<div style="background:#fff;border:1px solid #e8e5e0;border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="font-size:0.95rem;font-weight:500;color:#1a1a1a;">{email}</div><div style="font-size:0.75rem;color:#777;">{ts}</div></div><span class="badge {bc}">{status}</span></div><div style="font-size:0.68rem;color:#999;margin-top:0.4rem;">{case_id}</div></div>', unsafe_allow_html=True)
        if st.button("Open", key=f"btn_{case_id}"):
            st.session_state.selected_id = case_id
            st.rerun()

with col_detail:
    if st.session_state.selected_id:
        case = next((c for c in cases if c.get("case_id") == st.session_state.selected_id), None)
        if case:
            status = case.get("human_decision", {}).get("decision", "PENDING")
            rec = case.get("agent_outputs", {}).get("final_recommendation", "")
            st.markdown(f'<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;">{case["case_id"]} · Application Detail</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-section"><div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;"><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Student Email</div><div style="font-size:1rem;font-weight:500;">{case.get("student_email","?")}</div></div><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Date</div><div style="font-size:1rem;font-weight:500;">{case.get("timestamp","")[:10]}</div></div><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Status</div><div style="font-size:1rem;font-weight:500;">{status}</div></div></div></div>', unsafe_allow_html=True)

            st.markdown('<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;display:block;margin-bottom:0.5rem;">AI Recommendation</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)

            if status == "PENDING":
                st.markdown('<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;display:block;margin-bottom:0.5rem;">Coordinator Decision</span>', unsafe_allow_html=True)
                notes = st.text_area("Notes (optional)", key="notes_input", label_visibility="collapsed", placeholder="Add notes here...")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("✓ Approve", key="approve"):
                        update_human_decision(case["case_id"], "APPROVE", notes)
                        st.success("Approved.")
                        st.rerun()
                with b2:
                    if st.button("✕ Reject", key="reject"):
                        update_human_decision(case["case_id"], "REJECT", notes)
                        st.error("Rejected.")
                        st.rerun()
                with b3:
                    if st.button("↩ Clarify", key="clarify"):
                        update_human_decision(case["case_id"], "CLARIFY", notes)
                        st.info("Clarification requested.")
                        st.rerun()
            else:
                st.markdown(f'<div class="detail-section"><b>Decision:</b> {status}<br><b>Notes:</b> {case.get("human_decision",{}).get("notes","")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:300px;color:#ccc;font-size:0.9rem;">Select an application to view details</div>', unsafe_allow_html=True)
