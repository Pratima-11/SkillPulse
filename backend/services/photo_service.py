
"""Validate and store worker profile photographs."""

import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from models.worker_photo import WorkerPhoto

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PHOTO_SIZE = 2 * 1024 * 1024


def detect_image_extension(content):
    """Identify supported image formats from their file signatures."""
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"

    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    if (
        len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP"
    ):
        return ".webp"

    return None


def save_worker_photo(worker, uploaded_file, uploader_user_id):
    """Save a validated image and create or update its database record."""
    if not uploaded_file or not uploaded_file.filename:
        raise ValueError("Please select a photo to upload.")

    original_name = secure_filename(uploaded_file.filename)
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Use a JPG, JPEG, PNG, or WebP image.")

    content = uploaded_file.read(MAX_PHOTO_SIZE + 1)

    if not content:
        raise ValueError("The selected photo is empty.")

    if len(content) > MAX_PHOTO_SIZE:
        raise ValueError("Photo size must not exceed 2 MB.")

    actual_extension = detect_image_extension(content)

    if not actual_extension:
        raise ValueError("The file does not contain a supported image.")

    if extension in {".jpg", ".jpeg"} and actual_extension != ".jpg":
        raise ValueError("The file extension does not match its image format.")

    if extension != actual_extension and not (
        extension == ".jpeg" and actual_extension == ".jpg"
    ):
        raise ValueError("The file extension does not match its image format.")

    upload_dir = os.path.join(
        current_app.root_path, "uploads", "worker_photos"
    )
    os.makedirs(upload_dir, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}{actual_extension}"
    destination = os.path.join(upload_dir, stored_name)

    with open(destination, "wb") as photo_file:
        photo_file.write(content)

    existing = WorkerPhoto.query.filter_by(worker_id=worker.id).first()
    old_name = existing.file_name if existing else None

    if existing:
        existing.file_name = stored_name
        existing.uploaded_by_user_id = uploader_user_id
    else:
        existing = WorkerPhoto(
            worker_id=worker.id,
            file_name=stored_name,
            uploaded_by_user_id=uploader_user_id,
        )
        from app.extensions import db
        db.session.add(existing)

    return existing, old_name, destination
