import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Internship Coordinator", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background:#13151a; color:#f0f0f0; }
.stApp { background:#0a0a0a; }
.block-container { padding:2rem 2.5rem !important; max-width:1400px !important; }
.app-logo { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800;color:#fff; }
.app-logo span { color:#c8ff00; }
.divider { border:none; border-top:1px solid #1a1a1a; margin:1.5rem 0; }
.status-badge { display:inline-block; padding:3px 10px; border-radius:4px; font-size:0.75rem; font-weight:600; }
.badge-pending  { background:#1a1a00; color:#c8ff00; border:1px solid #c8ff00; }
.badge-approved { background:#0d1a00; color:#34d399; border:1px solid #a8d400; }
.badge-rejected { background:#1a0000; color:#ff8888; border:1px solid #ff4444; }
.badge-review   { background:#0d0d1a; color:#88aaff; border:1px solid #4466ff; }
.agent-box { background:#111; border:1px solid #222; border-radius:6px; padding:0.6rem 1rem; margin-bottom:0.4rem; font-size:0.82rem; }
.agent-done    { border-left:3px solid #a8d400; }
.agent-running { border-left:3px solid #c8ff00; }
.agent-waiting { border-left:3px solid #333; color:#555; }
section[data-testid="stSidebar"] { background:#0f0f0f !important; border-right:1px solid #1a1a1a !important; }
.stButton>button { background:#c8ff00 !important; color:#fff !important; border:none !important;
    border-radius:2px !important; font-family:'Syne',sans-serif !important; font-weight:700 !important;
    font-size:0.8rem !important; text-transform:uppercase !important; }
.stButton>button:hover { background:#fff !important; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Mock Data ─────────────────────────────────────────────────────────────────
APPLICATIONS = [
    {"id": "APP-001", "student": "Ali Yılmaz",    "company": "Google",    "date": "2026-05-10", "status": "Pending",  "agents_done": 3},
    {"id": "APP-002", "student": "Zeynep Kaya",   "company": "Microsoft", "date": "2026-05-11", "status": "Approved", "agents_done": 6},
    {"id": "APP-003", "student": "Emre Demir",    "company": "Amazon",    "date": "2026-05-12", "status": "Rejected", "agents_done": 6},
    {"id": "APP-004", "student": "Selin Arslan",  "company": "Meta",      "date": "2026-05-13", "status": "Review",   "agents_done": 4},
    {"id": "APP-005", "student": "Can Öztürk",    "company": "Apple",     "date": "2026-05-14", "status": "Pending",  "agents_done": 1},
]

AGENTS = [
    "Email Intake",
    "Document Extraction",
    "Completeness Validation",
    "University Rules",
    "Supervisor Verification",
    "Decision Recommendation",
]

# ── Session state ─────────────────────────────────────────────────────────────
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:1rem;">Filter</div>', unsafe_allow_html=True)
    status_filter = st.selectbox("Status", ["All", "Pending", "Approved", "Rejected", "Review"])
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:0.5rem;">Summary</div>', unsafe_allow_html=True)
    total     = len(APPLICATIONS)
    pending   = sum(1 for a in APPLICATIONS if a["status"] == "Pending")
    approved  = sum(1 for a in APPLICATIONS if a["status"] == "Approved")
    rejected  = sum(1 for a in APPLICATIONS if a["status"] == "Rejected")
    st.metric("Total",    total)
    st.metric("Pending",  pending)
    st.metric("Approved", approved)
    st.metric("Rejected", rejected)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-logo">Internship <span>Coordinator</span></div>', unsafe_allow_html=True)
st.markdown('<p style="color:#555;font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem;">ATA Builders Lab · Agentic System</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Application List ──────────────────────────────────────────────────────────
col_list, col_detail = st.columns([2, 3], gap="large")

with col_list:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:1rem;">Applications</div>', unsafe_allow_html=True)

    filtered = APPLICATIONS if status_filter == "All" else [a for a in APPLICATIONS if a["status"] == status_filter]

    for app in filtered:
        badge_class = {
            "Pending": "badge-pending",
            "Approved": "badge-approved",
            "Rejected": "badge-rejected",
            "Review": "badge-review",
        }.get(app["status"], "badge-pending")

        selected = st.session_state.selected_id == app["id"]
        border_color = "#c8ff00" if selected else "#222"

        st.markdown(f"""
        <div style="background:#111;border:1px solid {border_color};border-radius:6px;padding:0.8rem 1rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-weight:600;font-size:0.9rem;">{app['student']}</div>
                    <div style="color:#555;font-size:0.75rem;">{app['company']} · {app['date']}</div>
                </div>
                <span class="status-badge {badge_class}">{app['status']}</span>
            </div>
            <div style="color:#444;font-size:0.7rem;margin-top:0.4rem;">{app['id']} · Agents: {app['agents_done']}/6</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View", key=f"btn_{app['id']}"):
            st.session_state.selected_id = app["id"]
            st.rerun()

# ── Detail Panel ──────────────────────────────────────────────────────────────
with col_detail:
    if st.session_state.selected_id:
        app = next(a for a in APPLICATIONS if a["id"] == st.session_state.selected_id)
        st.markdown(f'<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:1rem;">{app["id"]} · Detail</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Student", app["student"])
            st.metric("Company", app["company"])
        with c2:
            st.metric("Date", app["date"])
            st.metric("Status", app["status"])

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:0.8rem;">Agent Pipeline</div>', unsafe_allow_html=True)

        for i, agent in enumerate(AGENTS):
            if i < app["agents_done"]:
                css = "agent-done"
                icon = "✔"
                color = "#a8d400"
            elif i == app["agents_done"]:
                css = "agent-running"
                icon = "⟳"
                color = "#c8ff00"
            else:
                css = "agent-waiting"
                icon = "○"
                color = "#333"
            st.markdown(f'<div class="agent-box {css}"><span style="color:{color};margin-right:8px;">{icon}</span>{agent}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.2em;color:#c8ff00;text-transform:uppercase;margin-bottom:0.8rem;">Coordinator Decision</div>', unsafe_allow_html=True)

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("✔ Approve", key="approve"):
                st.success("Approved!")
        with b2:
            if st.button("✘ Reject", key="reject"):
                st.error("Rejected!")
        with b3:
            if st.button("? Clarify", key="clarify"):
                st.info("Clarification requested!")
    else:
        st.markdown('<div style="color:#333;font-size:0.9rem;margin-top:3rem;text-align:center;">← Select an application to view details</div>', unsafe_allow_html=True)
