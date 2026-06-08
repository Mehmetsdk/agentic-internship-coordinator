import streamlit as st

st.set_page_config(page_title="Internship Coordinator", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #f7f6f3; color: #1a1a1a; }
.stApp { background: #f7f6f3; }
.block-container { padding: 2.5rem 3rem !important; max-width: 1300px !important; }
section[data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #e8e5e0 !important; }
.badge { display:inline-block; padding:2px 9px; border-radius:20px; font-size:0.7rem; font-weight:500; }
.badge-pending  { background:#fef9e7; color:#b7860c; border:1px solid #f5e49a; }
.badge-approved { background:#edfaf3; color:#1a7a45; border:1px solid #a8e6c0; }
.badge-rejected { background:#fef0f0; color:#c0392b; border:1px solid #f5b7b1; }
.badge-review   { background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; }
.detail-section { background:#fff; border:1px solid #e8e5e0; border-radius:8px; padding:1.2rem 1.4rem; margin-bottom:1rem; }
.agent-item { display:flex; align-items:center; gap:0.75rem; padding:0.6rem 0; border-bottom:1px solid #f0ede8; font-size:0.85rem; }
.agent-item:last-child { border-bottom:none; }
.agent-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.dot-done { background:#22c55e; } .dot-running { background:#f59e0b; } .dot-waiting { background:#e0ddd8; }
.stButton>button { font-family:'DM Sans',sans-serif !important; border-radius:6px !important; border:1px solid #e0ddd8 !important; background:#fff !important; color:#1a1a1a !important; width:100% !important; }
.stButton>button:hover { background:#1a1a1a !important; color:#fff !important; border-color:#1a1a1a !important; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

APPLICATIONS = [
    {"id": "APP-001", "student": "Ali Yılmaz",   "company": "Google",    "date": "2026-05-10", "status": "Pending",  "agents_done": 3},
    {"id": "APP-002", "student": "Zeynep Kaya",  "company": "Microsoft", "date": "2026-05-11", "status": "Approved", "agents_done": 6},
    {"id": "APP-003", "student": "Emre Demir",   "company": "Amazon",    "date": "2026-05-12", "status": "Rejected", "agents_done": 6},
    {"id": "APP-004", "student": "Selin Arslan", "company": "Meta",      "date": "2026-05-13", "status": "Review",   "agents_done": 4},
    {"id": "APP-005", "student": "Can Öztürk",   "company": "Apple",     "date": "2026-05-14", "status": "Pending",  "agents_done": 1},
]
AGENTS = ["Email Intake","Document Extraction","Completeness Validation","University Rules","Supervisor Verification","Decision Recommendation"]

if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

with st.sidebar:
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Filter</span>', unsafe_allow_html=True)
    status_filter = st.selectbox("Status", ["All","Pending","Approved","Rejected","Review"], label_visibility="collapsed")
    st.divider()
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Overview</span>', unsafe_allow_html=True)
    for label, val, color in [("Total",len(APPLICATIONS),"#1a1a1a"),("Pending",sum(1 for a in APPLICATIONS if a["status"]=="Pending"),"#b7860c"),("Approved",sum(1 for a in APPLICATIONS if a["status"]=="Approved"),"#1a7a45"),("Rejected",sum(1 for a in APPLICATIONS if a["status"]=="Rejected"),"#c0392b")]:
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #f0ede8;"><span style="font-size:0.82rem;color:#666;">{label}</span><span style="font-size:1.1rem;font-weight:600;color:{color};">{val}</span></div>', unsafe_allow_html=True)

st.markdown('<div style="margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid #e0ddd8;"><div style="font-family:Georgia,serif;font-size:2.4rem;color:#1a1a1a;letter-spacing:-0.02em;">Internship <em style="color:#6b6b6b;">Coordinator</em></div><div style="font-size:0.75rem;color:#777;letter-spacing:0.12em;text-transform:uppercase;margin-top:0.4rem;">ATA Builders Lab · Agentic System · CrewAI</div></div>', unsafe_allow_html=True)

col_list, col_detail = st.columns([2, 3], gap="large")
filtered = APPLICATIONS if status_filter == "All" else [a for a in APPLICATIONS if a["status"] == status_filter]

with col_list:
    st.markdown('<span style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa;">Applications</span>', unsafe_allow_html=True)
    for app in filtered:
        bc = {"Pending":"badge-pending","Approved":"badge-approved","Rejected":"badge-rejected","Review":"badge-review"}.get(app["status"],"badge-pending")
        st.markdown(f'<div style="background:#fff;border:1px solid #e8e5e0;border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="font-size:0.95rem;font-weight:500;color:#1a1a1a;">{app["student"]}</div><div style="font-size:0.75rem;color:#777;">{app["company"]} · {app["date"]}</div></div><span class="badge {bc}">{app["status"]}</span></div><div style="font-size:0.68rem;color:#999;margin-top:0.4rem;">{app["id"]} · {app["agents_done"]}/6 agents</div></div>', unsafe_allow_html=True)
        if st.button("Open", key=f"btn_{app['id']}"):
            st.session_state.selected_id = app["id"]
            st.rerun()

with col_detail:
    if st.session_state.selected_id:
        app = next(a for a in APPLICATIONS if a["id"] == st.session_state.selected_id)
        st.markdown(f'<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;">{app["id"]} · Application Detail</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-section"><div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;"><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Student</div><div style="font-size:1rem;font-weight:500;">{app["student"]}</div></div><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Company</div><div style="font-size:1rem;font-weight:500;">{app["company"]}</div></div><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Date</div><div style="font-size:1rem;font-weight:500;">{app["date"]}</div></div><div><div style="font-size:0.7rem;color:#888;text-transform:uppercase;">Status</div><div style="font-size:1rem;font-weight:500;">{app["status"]}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;">Agent Pipeline</span>', unsafe_allow_html=True)
        html = '<div class="detail-section">'
        for i, agent in enumerate(AGENTS):
            if i < app["agents_done"]: dot, nc, note = "dot-done", "color:#1a1a1a", "✓"
            elif i == app["agents_done"]: dot, nc, note = "dot-running", "color:#92400e;font-weight:500", "Running…"
            else: dot, nc, note = "dot-waiting", "color:#bbb", ""
            html += f'<div class="agent-item"><div class="agent-dot {dot}"></div><span style="{nc}">{agent}</span><span style="margin-left:auto;font-size:0.72rem;color:#bbb;">{note}</span></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('<span style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa;display:block;margin-bottom:0.5rem;">Coordinator Decision</span>', unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("✓ Approve", key="approve"): st.success("Approved.")
        with b2:
            if st.button("✕ Reject", key="reject"): st.error("Rejected.")
        with b3:
            if st.button("↩ Clarify", key="clarify"): st.info("Clarification requested.")
    else:
        st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:300px;color:#ccc;font-size:0.9rem;">Select an application to view details</div>', unsafe_allow_html=True)
