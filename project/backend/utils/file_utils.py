"""File utility helpers for upload validation and temporary storage."""

from pathlib import Path
from uuid import uuid4


ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"


def is_allowed_file(filename):
    """Check whether the uploaded filename has an allowed extension."""
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_dir():
    """Create the upload directory if it does not already exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def build_temp_filename(filename):
    """Build a unique temporary filename while keeping the original extension."""
    suffix = Path(filename).suffix
    return f"{uuid4().hex}{suffix}"


def get_temp_file_path(filename):
    """Return the full path where an uploaded file should be stored temporarily."""
    ensure_upload_dir()
    return UPLOAD_DIR / build_temp_filename(filename)