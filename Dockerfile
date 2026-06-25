FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-tur libglib2.0-0 fonts-liberation \
    supervisor curl git nginx \
    && curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update && apt-get install -y ngrok \
    && rm -rf /var/lib/apt/lists/*

# Clone PDF Anonymizer from GitHub
RUN git clone https://github.com/Mehmetsdk/PDF---Anonymizer.git /app/PDF---Anonymizer

WORKDIR /app/coordinator
COPY . .

RUN pip install --no-cache-dir \
    "crewai[anthropic]" \
    fastapi uvicorn pydantic python-dotenv \
    streamlit \
    PyMuPDF Pillow Faker pdfplumber pytesseract

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /app/coordinator/logs

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
