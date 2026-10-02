"""
Generic job endpoints (used mainly by workers browsing/filtering, and for
applying to a job).

GET  /api/jobs                 - list/filter open jobs
GET  /api/jobs/<id>             - job detail
POST /api/jobs/<id>/apply       - worker applies to a job
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.config import Config
from models.job import Job
from models.job_application import JobApplication
from models.worker_profile import WorkerProfile
from models.notification import Notification
from utils.decorators import role_required
from utils.validators import ValidationError
from services.matching_service import rank_workers_for_job
from services.distance_service import haversine_distance_km

job_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@job_bp.route("", methods=["GET"])
def list_jobs():
    """
    Query params (all optional):
      skill=Painter, area=Koramangala, max_distance_km=10, lat=.., lng=..,
      min_wage=500, date=2026-09-27, min_experience=2
    Only returns jobs still open for applications.
    """
    query = Job.query.filter(Job.status.in_(["POSTED", "MATCHING", "APPLICANTS"]))

    skill_name = request.args.get("skill")
    if skill_name:
        query = query.join(Job.skill).filter_by(name=skill_name)

    min_wage = request.args.get("min_wage", type=float)
    if min_wage is not None:
        query = query.filter(Job.wage >= min_wage)

    job_date = request.args.get("date")
    if job_date:
        query = query.filter(Job.job_date == job_date)

    area = request.args.get("area")
    if area:
        query = query.filter(Job.area_text.ilike(f"%{area.strip()}%"))

    min_experience = request.args.get("min_experience", type=float)
    if min_experience is not None:
        query = query.filter(Job.min_experience <= min_experience)

    jobs = query.order_by(Job.job_date.asc()).all()

    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    max_distance = request.args.get("max_distance_km", type=float)

    results = []
    for job in jobs:
        job_dict = job.to_dict()
        if lat is not None and lng is not None:
            distance = haversine_distance_km(lat, lng, job.latitude, job.longitude)
            if max_distance is not None and distance > max_distance:
                continue
            job_dict["distance_km"] = round(distance, 2)
        results.append(job_dict)

    return jsonify({"jobs": results}), 200


@job_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404
    return jsonify({"job": job.to_dict()}), 200


@job_bp.route("/<int:job_id>/apply", methods=["POST"])
@role_required("worker")
def apply_to_job(job_id):
    """
    Worker explicitly applies to a job. The match score is (re)computed at
    apply-time and stored, so the score shown is always explainable and
    never stale.
    """
    user_id = get_jwt_identity()
    profile = WorkerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "Worker profile not found."}), 404

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404

    if job.status not in ("POSTED", "MATCHING", "APPLICANTS"):
        return jsonify({"error": "This job is no longer accepting applications."}), 400

    existing = JobApplication.query.filter_by(job_id=job.id, worker_id=profile.id).first()
    if existing:
        return jsonify({"error": "You have already applied to this job."}), 400

    ranked = rank_workers_for_job(job, [profile], Config.MATCHING_WEIGHTS_PATH)
    if not ranked:
        return jsonify({
            "error": "You do not meet the requirements for this job "
                     "(skill, availability, or distance)."
        }), 400

    entry = ranked[0]
    application = JobApplication(
        job_id=job.id,
        worker_id=profile.id,
        match_score=entry["match_score"],
        score_breakdown=entry["breakdown"],
        status="PENDING",
    )
    db.session.add(application)

    if job.status == "POSTED":
        job.status = "MATCHING"

    notification = Notification(
        user_id=job.contractor.user_id,
        message=f"A new worker applied to your job #{job.id}.",
        notif_type="NEW_APPLICATION",
    )
    db.session.add(notification)

    db.session.commit()
    return jsonify({"application": application.to_dict(), "reasons": entry["reasons"]}), 201
