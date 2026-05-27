"""Upload routes — receive a document, run all extractors + NLP, return unified JSON."""

from pathlib import Path

from flask import Blueprint, jsonify, request

from services.extraction_service import extract_document_data, extract_images, extract_tables
from services.nlp_service import extract_entities, extract_summary
from services.ocr_service import needs_ocr, ocr_image, ocr_pdf
from utils.file_utils import get_temp_file_path, is_allowed_file

upload_bp = Blueprint("upload_bp", __name__)


def _run_nlp(result):
    """Attach NLP results (entities + summary) to an existing extraction dict in-place."""
    text = result.get("text", "")
    result["entities"] = extract_entities(text)
    result["summary"] = extract_summary(text, num_sentences=5)
    return result


@upload_bp.post("/upload")
def upload_document():
    """Save the file, detect type, run extraction + NLP, return all results."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file.filename:
        return jsonify({"error": "Empty filename."}), 400

    if not is_allowed_file(uploaded_file.filename):
        return jsonify({"error": "File type not allowed. Use PDF, PNG, JPG, or JPEG."}), 400

    temp_path = get_temp_file_path(uploaded_file.filename)
    uploaded_file.save(temp_path)

    try:
        ext = Path(uploaded_file.filename).suffix.lower()

        if ext == ".pdf":
            result = extract_document_data(temp_path)
            # extract_document_data uses the UUID temp name — restore the real one.
            result["file_name"] = uploaded_file.filename

            # Scanned PDFs have no text layer — fall back to OCR.
            if needs_ocr(result["text"]):
                ocr_result = ocr_pdf(temp_path)
                result["text"] = ocr_result["text"]
                result["pages"] = ocr_result["pages"]
                result["ocr_used"] = True
                result["document_type"] = "scanned"
            else:
                result["ocr_used"] = False
                result["document_type"] = "digital"

            result["tables"] = extract_tables(temp_path)
            result["images"] = extract_images(temp_path)
            _run_nlp(result)
            return jsonify(result)

        # Image uploads always use OCR.
        ocr_result = ocr_image(temp_path)
        result = {
            "file_name": uploaded_file.filename,
            "page_count": ocr_result["page_count"],
            "metadata": {},
            "text": ocr_result["text"],
            "pages": ocr_result["pages"],
            "tables": [],
            "images": [],
            "ocr_used": True,
            "document_type": "image",
        }
        _run_nlp(result)
        return jsonify(result)

    except Exception as exc:
        return jsonify({"error": f"Extraction failed: {str(exc)}"}), 500

    finally:
        if temp_path.exists():
            temp_path.unlink()
