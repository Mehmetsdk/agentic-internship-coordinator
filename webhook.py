"""Webhook server — receives n8n triggers and runs the internship pipeline."""

import json
import os
import sys
import tempfile
import threading
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Run: pip install fastapi uvicorn pydantic")
    sys.exit(1)

app = FastAPI(title="Internship Coordinator Webhook")

PYTHON = sys.executable


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

        # If PDF content sent as base64, save it to a temp file
        if payload.pdf_content:
            import base64
            raw = payload.pdf_content
            # Strip data-URL prefix if present (e.g. "data:application/pdf;base64,...")
            if "," in raw and raw.startswith("data:"):
                raw = raw.split(",", 1)[1]
            # Add padding if needed
            raw += "=" * (-len(raw) % 4)
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp.write(base64.b64decode(raw))
            tmp.close()
            pdf_path = tmp.name
        elif payload.pdf_path:
            pdf_path = payload.pdf_path
        else:
            raise HTTPException(status_code=400, detail="No PDF provided")

        result = run_pipeline(
            pdf_path=pdf_path,
            student_email=payload.student_email,
        )

        return JSONResponse(content={
            "status": "processed",
            "decision": result.get("decision", "UNKNOWN"),
            "notes": result.get("notes", ""),
            "student_email": payload.student_email,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8503))
    print(f"Webhook server starting on http://localhost:{port}")
    print(f"  POST http://localhost:{port}/webhook/application")
    uvicorn.run(app, host="0.0.0.0", port=port)
