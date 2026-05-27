FROM python:3.11-slim

# System packages:
#   tesseract-ocr      — OCR engine used by pytesseract
#   tesseract-ocr-eng  — English language data for Tesseract
#   libgl1 + libglib2.0-0 — required by opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer-cached until requirements change).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models — md preferred, sm available as fallback.
RUN python -m spacy download en_core_web_sm && python -m spacy download en_core_web_md

# Copy application source.
COPY . .

# Ensure upload/output directories exist inside the container.
RUN mkdir -p uploads outputs

EXPOSE 10000

# 1 worker + preload: app (including spaCy en_core_web_md ~200 MB) loads once before
# the worker forks, keeping total RAM inside Render free tier's 512 MB limit.
CMD gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120 --preload app:app
