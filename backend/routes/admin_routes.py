"""
Admin-facing endpoints.

GET  /api/admin/stats
GET  /api/admin/workers
POST /api/admin/workers/<id>/verify
GET  /api/admin/contractors
GET  /api/admin/jobs
POST /api/admin/users/<id>/deactivate
POST /api/admin/users/<id>/activate
"""

from flask import Blueprint, request, jsonify

from app.extensions import db
from models.user import User
from models.worker_profile import WorkerProfile
from models.contractor_profile import ContractorProfile
from models.job import Job
from utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@role_required("admin")
def stats():
    return jsonify({
        "total_workers": WorkerProfile.query.count(),
        "total_contractors": ContractorProfile.query.count(),
        "total_jobs": Job.query.count(),
        "active_jobs": Job.query.filter(
            Job.status.in_(["POSTED", "MATCHING", "APPLICANTS", "WORKER_SELECTED", "CONFIRMED", "IN_PROGRESS"])
        ).count(),
        "completed_jobs": Job.query.filter_by(status="COMPLETED").count(),
        "verified_workers": WorkerProfile.query.filter_by(verification_status="verified").count(),
        "pending_verification": WorkerProfile.query.filter_by(verification_status="pending").count(),
    }), 200


@admin_bp.route("/workers", methods=["GET"])
@role_required("admin")
def list_workers():
    status_filter = request.args.get("verification_status")
    query = WorkerProfile.query
    if status_filter:
        query = query.filter_by(verification_status=status_filter)
    workers = query.all()
    return jsonify({"workers": [w.to_dict() for w in workers]}), 200


@admin_bp.route("/workers/<int:worker_id>/verify", methods=["POST"])
@role_required("admin")
def verify_worker(worker_id):
    """Request body: { "verification_status": "verified" | "rejected" }"""
    data = request.get_json(silent=True) or {}
    new_status = data.get("verification_status")
    if new_status not in ("verified", "rejected", "pending"):
        return jsonify({"error": "verification_status must be verified, rejected, or pending."}), 400

    worker = WorkerProfile.query.get(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found."}), 404

    worker.verification_status = new_status
    db.session.commit()
    return jsonify({"worker": worker.to_dict()}), 200


@admin_bp.route("/contractors", methods=["GET"])
@role_required("admin")
def list_contractors():
    contractors = ContractorProfile.query.all()
    return jsonify({"contractors": [c.to_dict() for c in contractors]}), 200


@admin_bp.route("/jobs", methods=["GET"])
@role_required("admin")
def list_all_jobs():
    status_filter = request.args.get("status")
    query = Job.query
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@role_required("admin")
def deactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    user.is_active = False
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 200


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@role_required("admin")
def activate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    user.is_active = True
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 200
