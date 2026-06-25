"""Webhook server — receives n8n triggers and runs the internship pipeline."""

import json
import os
import re
import sys
import threading
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    from typing import Optional
    import uvicorn
except ImportError:
    print("Run: pip install fastapi uvicorn pydantic")
    sys.exit(1)

app = FastAPI(title="Internship Coordinator Webhook")

PYTHON = sys.executable


def _clean_email(raw: str) -> str:
    """Extract a valid email from n8n output (which may be '[object Object]' or '=email@x.com')."""
    if not raw or not isinstance(raw, str):
        return "unknown@unknown.com"
    if "[object" in raw.lower():
        return "unknown@unknown.com"
    # Strip leading = that n8n sometimes adds (expression mode artifact)
    cleaned = raw.strip().lstrip("=").strip()
    m = re.search(r'[\w.+%-]+@[\w.-]+\.[a-zA-Z]{2,}', cleaned)
    return m.group(0) if m else "unknown@unknown.com"


class ApplicationPayload(BaseModel):
    student_email: str
    pdf_content: str | None = None   # base64 encoded PDF from n8n
    pdf_path: str | None = None      # local path (for local testing)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook/application")
def receive_application(payload: ApplicationPayload):
    """Receive an internship application from n8n and run the agent pipeline."""
    try:
        from main import run_pipeline

        # If PDF content sent as base64, save it to a permanent location
        if payload.pdf_content:
            import base64
            from datetime import datetime
            raw = payload.pdf_content
            # Strip data-URL prefix if present (e.g. "data:application/pdf;base64,...")
            if "," in raw and raw.startswith("data:"):
                raw = raw.split(",", 1)[1]
            # Add padding if needed
            raw += "=" * (-len(raw) % 4)
            pdfs_dir = Path(__file__).parent / "logs" / "pdfs"
            pdfs_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_email = re.sub(r'[^\w@.-]', '_', _clean_email(payload.student_email))
            pdf_path = str(pdfs_dir / f"{ts}_{safe_email}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(base64.b64decode(raw))
        elif payload.pdf_path:
            pdf_path = payload.pdf_path
        else:
            raise HTTPException(status_code=400, detail="No PDF provided")

        student_email = _clean_email(payload.student_email)

        result = run_pipeline(
            pdf_path=pdf_path,
            student_email=student_email,
        )

        return JSONResponse(content={
            "status": "processed",
            "decision": result.get("decision", "UNKNOWN"),
            "notes": result.get("notes", ""),
            "student_email": payload.student_email,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/upload")
async def receive_application_upload(
    student_email: str = Form(...),
    pdf_file: Optional[UploadFile] = File(None),
):
    """Form-data endpoint — receives binary PDF directly from n8n."""
    import asyncio
    from datetime import datetime
    try:
        student_email_clean = _clean_email(student_email)

        if not pdf_file:
            raise HTTPException(status_code=400, detail="No PDF file provided")

        pdfs_dir = Path(__file__).parent / "logs" / "pdfs"
        pdfs_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = re.sub(r'[^\w@.-]', '_', student_email_clean)
        pdf_path = str(pdfs_dir / f"{ts}_{safe_email}.pdf")

        contents = await pdf_file.read()
        with open(pdf_path, "wb") as f:
            f.write(contents)

        # run_pipeline uses crewai's synchronous kickoff() which conflicts with
        # FastAPI's event loop — run it in a thread pool to avoid the conflict
        from main import run_pipeline
        result = await asyncio.to_thread(run_pipeline, pdf_path=pdf_path, student_email=student_email_clean)

        return JSONResponse(content={
            "status": "processed",
            "decision": result.get("decision", "UNKNOWN"),
            "student_email": student_email_clean,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("WEBHOOK_PORT", 8503))
    print(f"Webhook server starting on http://localhost:{port}")
    print(f"  POST http://localhost:{port}/webhook/application  (JSON)")
    print(f"  POST http://localhost:{port}/webhook/upload        (Form-data binary)")
    uvicorn.run(app, host="0.0.0.0", port=port)
