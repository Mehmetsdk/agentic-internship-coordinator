FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-tur libglib2.0-0 fonts-liberation \
    supervisor curl git nginx unzip \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz -C /usr/local/bin

# Clone PDF Anonymizer from GitHub
RUN git clone https://github.com/Mehmetsdk/PDF---Anonymizer.git /app/PDF---Anonymizer

WORKDIR /app/coordinator
COPY . .

RUN pip install --no-cache-dir \
    "crewai[anthropic]" \
    fastapi uvicorn pydantic python-dotenv \
    streamlit \
    PyMuPDF Pillow Faker pdfplumber pytesseract \
    gspread google-auth \
    "langfuse>=2,<3"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /app/coordinator/logs

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
