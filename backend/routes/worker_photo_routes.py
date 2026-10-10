
"""Worker and admin-assisted profile photo upload routes."""

import os

from flask import Blueprint, current_app, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from models.worker_profile import WorkerProfile
from models.worker_photo import WorkerPhoto
from services.photo_service import save_worker_photo, MAX_PHOTO_SIZE
from utils.decorators import role_required

worker_photo_bp = Blueprint(
    "worker_photo",
    __name__,
    url_prefix="/api",
)


def _upload_photo(worker, uploader_user_id):
    uploaded_file = __import__("flask").request.files.get("photo")

    if not uploaded_file:
        return jsonify({"error": "Please select a photo to upload."}), 400

    try:
        photo, old_name, destination = save_worker_photo(
            worker, uploaded_file, uploader_user_id
        )
        db.session.commit()

        # Delete the old file only after the new database record is saved.
        if old_name and old_name != photo.file_name:
            old_path = os.path.join(
                current_app.root_path, "uploads", "worker_photos", old_name
            )
            if os.path.isfile(old_path):
                os.remove(old_path)

        return jsonify({
            "message": "Worker photo uploaded successfully.",
            "worker_id": worker.id,
            "photo_url": f"/api/worker-photos/{worker.id}",
        }), 200

    except ValueError as exc:
        db.session.rollback()
        if "destination" in locals() and os.path.isfile(destination):
            os.remove(destination)
        return jsonify({"error": str(exc)}), 400
    except Exception:
        db.session.rollback()
        if "destination" in locals() and os.path.isfile(destination):
            os.remove(destination)
        current_app.logger.exception("Worker photo upload failed")
        return jsonify({"error": "Photo upload failed. Please try again."}), 500


@worker_photo_bp.route("/worker/photo", methods=["POST"])
@role_required("worker")
def upload_my_photo():
    user_id = get_jwt_identity()
    worker = WorkerProfile.query.filter_by(user_id=user_id).first()

    if not worker:
        return jsonify({"error": "Worker profile not found."}), 404

    return _upload_photo(worker, user_id)


@worker_photo_bp.route("/admin/workers/<int:worker_id>/photo", methods=["POST"])
@role_required("admin")
def admin_upload_worker_photo(worker_id):
    worker = WorkerProfile.query.get(worker_id)

    if not worker:
        return jsonify({"error": "Worker not found."}), 404

    return _upload_photo(worker, get_jwt_identity())


@worker_photo_bp.route("/worker-photos/<int:worker_id>", methods=["GET"])
@role_required("worker", "contractor", "admin")
def get_worker_photo(worker_id):
    photo = WorkerPhoto.query.filter_by(worker_id=worker_id).first()

    if not photo:
        return jsonify({"error": "Photo not found."}), 404

    directory = os.path.join(
        current_app.root_path, "uploads", "worker_photos"
    )

    response = send_from_directory(
        directory, photo.file_name, conditional=True, max_age=300
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, max-age=300"
    return response
