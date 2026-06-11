# Agentic Internship Coordinator System 🎓

A multi-agent system built with **CrewAI** that automatically processes internship applications. The system reads a student's PDF application, runs it through a 6-agent pipeline, and presents a recommendation to a human coordinator for final approval.

---

## How It Works

```
Student Email + PDF
        ↓
[Agent 1] Email Intake
        ↓
[Agent 2] Document Extraction
        ↓
[Agent 3] Completeness Validation
        ↓
[Agent 4] University Rules Check
        ↓
[Agent 5] Supervisor Verification
        ↓
[Agent 6] Decision Recommendation
        ↓
Human Coordinator → APPROVE / REJECT / REQUEST CLARIFICATION
        ↓
Audit Log
```

---

## Agents

| Agent | Role |
|-------|------|
| Email Intake | Receives and confirms the application email and PDF |
| Document Extraction | Extracts student and company data from the PDF |
| Completeness Validation | Checks for missing or incomplete fields |
| University Rules | Validates compliance with university regulations |
| Supervisor Verification | Drafts a verification email to the company supervisor if needed |
| Decision Recommendation | Produces a final APPROVE / REJECT / CLARIFY recommendation |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | CrewAI |
| LLM | Groq (llama-3.3-70b-versatile) |
| UI Dashboard | Streamlit |
| Audit Logging | JSON (logs/ folder) |
| Language | Python 3.10+ |

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/Mehmetsdk/agentic-internship-coordinator.git
cd agentic-internship-coordinator
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Usage

**Run the agent pipeline:**
```bash
python main.py
```

**Run the coordinator dashboard:**
```bash
streamlit run dashboard.py
```

The dashboard shows all processed applications, agent pipeline progress, and allows the coordinator to approve, reject, or request clarification.

---

## Project Structure

```
agentic-internship-coordinator/
├── agents/                  # Individual agent definitions
├── templates/               # Email templates
├── test_data/               # Sample PDFs for testing
├── tests/                   # Unit tests
├── tools/                   # Custom CrewAI tools
├── main.py                  # Pipeline entry point
├── dashboard.py             # Streamlit coordinator UI
├── human_review.py          # Human-in-the-loop decision handler
├── audit_logger.py          # Logs all cases to JSON
├── AGENT_CONTRACTS.md       # Agent input/output contracts
└── requirements.txt
```

---

## Team

| Name | Role |
|------|------|
| Mehmet | Backend — Agent pipeline, CrewAI setup |
| Aysel | UI — Streamlit coordinator dashboard |
| Can | PDF & Email processing agents |
| Sami | Testing & documentation |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | API key for Groq LLM |

---

*ATA Builders Lab · Agentic Internship Coordinator · CrewAI*

