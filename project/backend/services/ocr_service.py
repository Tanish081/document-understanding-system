"""OCR service — Tesseract via pytesseract, page rendering via PyMuPDF.

PyMuPDF is used for PDF-to-image rendering to avoid the Poppler dependency.
OpenCV preprocessing improves recognition on scanned/compressed documents.

Image pipeline improvements:
  - RGBA PNGs are flattened against a white background before grayscaling.
  - Images smaller than 1400 px wide are upscaled with LANCZOS before OCR
    because Tesseract accuracy drops sharply below ~150 DPI equivalent.
  - PDFs use PSM 6 (uniform text block); standalone images use PSM 3
    (fully automatic layout detection) which handles mixed layouts better.
"""

import io
import platform
from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image


# ── Tesseract path ────────────────────────────────────────────────────────────

_TESSERACT_READY = False
_TESSERACT_ERROR = None


def _configure_tesseract():
    global _TESSERACT_READY, _TESSERACT_ERROR

    if platform.system() != "Windows":
        _TESSERACT_READY = True
        return

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe",
        Path.home() / "AppData" / "Local" / "Tesseract-OCR" / "tesseract.exe",
    ]
    for path in candidates:
        if Path(path).exists():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            _TESSERACT_READY = True
            return

    _TESSERACT_ERROR = (
        "Tesseract is not installed.\n"
        "Download and install it from:\n"
        "  https://github.com/UB-Mannheim/tesseract/wiki\n"
        "Choose the Windows installer, run it, then restart the Flask server."
    )


_configure_tesseract()


def _require_tesseract():
    if not _TESSERACT_READY:
        raise EnvironmentError(_TESSERACT_ERROR)


# ── Image preprocessing ───────────────────────────────────────────────────────

def _flatten_alpha(pil_image):
    """Composite RGBA/LA images onto a white background before grayscaling.

    Transparent PNGs produce black regions when converted directly to RGB,
    which confuses the threshold step and degrades OCR accuracy.
    """
    if pil_image.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", pil_image.size, (255, 255, 255))
        if pil_image.mode == "LA":
            pil_image = pil_image.convert("RGBA")
        bg.paste(pil_image, mask=pil_image.split()[3])
        return bg
    return pil_image.convert("RGB")


def _upscale_if_small(pil_image, min_width=1400):
    """Upscale images narrower than min_width using LANCZOS interpolation.

    Tesseract's accuracy drops sharply below roughly 150 DPI equivalent
    (~1000–1400 px for A4).  Upscaling is cheap and consistently improves
    recognition on compressed photos and low-res scans.
    """
    w, h = pil_image.size
    if w < min_width:
        scale = min_width / w
        new_size = (int(w * scale), int(h * scale))
        pil_image = pil_image.resize(new_size, Image.LANCZOS)
    return pil_image


def _preprocess(pil_image):
    """Convert a PIL image to a preprocessed numpy array for Tesseract.

    Pipeline: flatten alpha → upscale → grayscale → denoise → adaptive threshold.
    """
    pil_image = _flatten_alpha(pil_image)
    pil_image = _upscale_if_small(pil_image)

    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)

    # Mild denoising — h=10 removes grain without blurring text edges.
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # Adaptive threshold handles uneven lighting (common in scanned docs / photos).
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 11,
    )
    return thresh


def _pil_from_fitz_page(page, dpi=300):
    """Render a PyMuPDF page to a PIL Image at the given DPI."""
    zoom = dpi / 72
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.open(io.BytesIO(pixmap.tobytes("png")))


# ── Public helpers ────────────────────────────────────────────────────────────

def needs_ocr(text, min_chars=30):
    """Return True when PyMuPDF found too little text to be a digital PDF."""
    return len(text.replace(" ", "").replace("\n", "")) < min_chars


def ocr_pdf(file_path, dpi=300):
    """OCR each page of a PDF using PyMuPDF rendering + Tesseract PSM 6."""
    _require_tesseract()
    document = fitz.open(str(file_path))
    pages = []
    full_text_parts = []

    try:
        for page_number, page in enumerate(document, start=1):
            pil_image = _pil_from_fitz_page(page, dpi=dpi)
            preprocessed = _preprocess(pil_image)
            page_text = pytesseract.image_to_string(
                preprocessed, config="--psm 6 --oem 3",
            ).strip()
            pages.append({"page_number": page_number, "text": page_text})
            full_text_parts.append(page_text)
    finally:
        document.close()

    return {
        "page_count": len(pages),
        "text": "\n\n".join(full_text_parts),
        "pages": pages,
        "ocr_used": True,
    }


def ocr_image(file_path):
    """OCR a single image file (PNG / JPG / JPEG) using Tesseract PSM 3.

    PSM 3 (fully automatic page segmentation) works better than PSM 6 for
    standalone images because it does not assume a single uniform text block.
    """
    _require_tesseract()
    pil_image = Image.open(str(file_path))
    preprocessed = _preprocess(pil_image)

    text = pytesseract.image_to_string(
        preprocessed, config="--psm 3 --oem 3",
    ).strip()

    return {
        "page_count": 1,
        "text": text,
        "pages": [{"page_number": 1, "text": text}],
        "ocr_used": True,
    }
