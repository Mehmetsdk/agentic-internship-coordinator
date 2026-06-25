FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-tur libglib2.0-0 fonts-liberation \
    supervisor curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy PDF Anonymizer modules
COPY ../PDF---Anonymizer /app/PDF---Anonymizer

# Copy coordinator project
COPY . /app/coordinator

WORKDIR /app/coordinator

# Install coordinator dependencies
RUN pip install --no-cache-dir \
    "crewai[anthropic]" \
    fastapi uvicorn pydantic python-dotenv \
    streamlit \
    PyMuPDF Pillow Faker pdfplumber pytesseract

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /app/coordinator/logs

EXPOSE 8501 8503

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
