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

# Download the spaCy medium model (better NER accuracy than sm).
RUN python -m spacy download en_core_web_md

# Copy application source.
COPY . .

# Ensure upload/output directories exist inside the container.
RUN mkdir -p uploads outputs

EXPOSE 5000

# gunicorn: 2 workers, 120 s timeout (OCR on large PDFs can be slow).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
