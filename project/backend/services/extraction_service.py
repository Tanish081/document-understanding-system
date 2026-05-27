"""Document extraction helpers — text/images via PyMuPDF, tables via pdfplumber."""

import base64
from pathlib import Path

import fitz
import pdfplumber


def extract_document_data(file_path):
    """Extract text, metadata, and page count from a PDF using PyMuPDF."""
    pdf_path = Path(file_path)
    document = fitz.open(pdf_path)

    try:
        pages = []
        full_text_parts = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")
            pages.append({"page_number": page_number, "text": page_text})
            full_text_parts.append(page_text)

        return {
            "file_name": pdf_path.name,
            "page_count": document.page_count,
            "metadata": document.metadata,
            "text": "\n".join(full_text_parts).strip(),
            "pages": pages,
        }
    finally:
        document.close()


def extract_tables(file_path):
    """Extract tables from every page of a PDF using pdfplumber.

    Returns a list of table dicts, each containing the page number, table index
    within that page, and a list-of-lists of cell strings.
    """
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_tables = page.extract_tables()
            for table_idx, raw_table in enumerate(page_tables):
                # pdfplumber can return None for empty cells — normalise to "".
                cleaned_rows = [
                    [cell if cell is not None else "" for cell in row]
                    for row in raw_table
                    if row  # skip any completely empty rows
                ]
                if cleaned_rows:
                    tables.append({
                        "page": page_number,
                        "table_index": table_idx,
                        "rows": cleaned_rows,
                    })
    return tables


def extract_images(file_path):
    """Extract embedded images from a PDF using PyMuPDF.

    Images smaller than 80×80 px are skipped — they are usually decorative
    icons or artefacts rather than meaningful figures.  Each image is returned
    as a base64-encoded data-URI so the frontend can render it directly.
    """
    images = []
    document = fitz.open(file_path)

    try:
        seen_xrefs = set()  # deduplicate images that appear on multiple pages

        for page_number, page in enumerate(document, start=1):
            for img_idx, img_info in enumerate(page.get_images(full=True)):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                base_image = document.extract_image(xref)
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                if width < 80 or height < 80:
                    continue  # skip tiny decorative elements

                ext = base_image["ext"]
                b64 = base64.b64encode(base_image["image"]).decode("utf-8")

                images.append({
                    "page": page_number,
                    "image_index": img_idx,
                    "ext": ext,
                    "width": width,
                    "height": height,
                    "data": f"data:image/{ext};base64,{b64}",
                })
    finally:
        document.close()

    return images
