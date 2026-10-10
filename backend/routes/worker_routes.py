"""
Worker-facing endpoints.

GET  /api/worker/profile
PUT  /api/worker/profile
POST /api/worker/skills
POST /api/worker/availability
GET  /api/worker/jobs/recommended
GET  /api/worker/applications
GET  /api/worker/dashboard-stats
"""

from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.config import Config
from models.worker_profile import WorkerProfile
from models.skill import Skill
from models.availability import Availability
from models.job import Job
from models.job_application import JobApplication
from utils.decorators import role_required
from utils.validators import (
    ValidationError, validate_positive_number, validate_latitude,
    validate_longitude, validate_date_not_past, require_fields,
)
from services.matching_service import rank_workers_for_job

worker_bp = Blueprint("worker", __name__, url_prefix="/api/worker")


def _get_current_worker_profile():
    user_id = get_jwt_identity()
    profile = WorkerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        raise ValidationError("Worker profile not found for this account.")
    return profile


@worker_bp.route("/profile", methods=["GET"])
@role_required("worker")
def get_profile():
    try:
        profile = _get_current_worker_profile()
        return jsonify({"profile": profile.to_dict()}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404


@worker_bp.route("/profile", methods=["PUT"])
@role_required("worker")
def update_profile():
    """
    Request body (all optional): full_name, phone, latitude, longitude,
    area_text, expected_wage, experience_years
    """
    data = request.get_json(silent=True) or {}
    try:
        profile = _get_current_worker_profile()

        if "full_name" in data:
            profile.full_name = data["full_name"]
        if "phone" in data:
            profile.phone = data["phone"]
        if "area_text" in data:
            profile.area_text = data["area_text"]
        if "latitude" in data:
            profile.latitude = validate_latitude(data["latitude"])
        if "longitude" in data:
            profile.longitude = validate_longitude(data["longitude"])
        if "expected_wage" in data:
            profile.expected_wage = validate_positive_number(data["expected_wage"], "expected_wage")
        if "experience_years" in data:
            profile.experience_years = validate_positive_number(
                data["experience_years"], "experience_years"
            )

        db.session.commit()
        return jsonify({"profile": profile.to_dict()}), 200
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@worker_bp.route("/skills", methods=["POST"])
@role_required("worker")
def update_skills():
    """
    Request body: { "skill_names": ["Painter", "Mason"] }
    Creates any skill that doesn't already exist, then sets the worker's
    skill list to exactly this set (replaces, does not merely append).
    """
    data = request.get_json(silent=True) or {}
    skill_names = data.get("skill_names")
    if not isinstance(skill_names, list) or not skill_names:
        return jsonify({"error": "skill_names must be a non-empty list."}), 400

    try:
        profile = _get_current_worker_profile()
        skills = []
        for name in skill_names:
            name_clean = str(name).strip()
            if not name_clean:
                continue
            skill = Skill.query.filter_by(name=name_clean).first()
            if not skill:
                skill = Skill(name=name_clean)
                db.session.add(skill)
                db.session.flush()
            skills.append(skill)

        profile.skills = skills
        db.session.commit()
        return jsonify({"profile": profile.to_dict()}), 200
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 404


@worker_bp.route("/availability", methods=["POST"])
@role_required("worker")
def set_availability():
    """
    Request body: { "available_date": "2026-09-27", "is_available": true }
    Upserts the availability row for that date.
    """
    data = request.get_json(silent=True) or {}
    try:
        require_fields(data, ["available_date"])
        parsed_date = validate_date_not_past(data["available_date"], "available_date")
        is_available = bool(data.get("is_available", True))

        profile = _get_current_worker_profile()
        row = Availability.query.filter_by(
            worker_id=profile.id, available_date=parsed_date
        ).first()
        if row:
            row.is_available = is_available
        else:
            row = Availability(
                worker_id=profile.id, available_date=parsed_date, is_available=is_available
            )
            db.session.add(row)

        db.session.commit()
        return jsonify({"availability": row.to_dict()}), 200
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@worker_bp.route("/jobs/recommended", methods=["GET"])
@role_required("worker")
def recommended_jobs():
    """
    Returns every currently-open job the worker qualifies for, ranked by
    match score, using the same matching engine the contractor side uses
    (run "in reverse" - one worker against many jobs).
    """
    try:
        profile = _get_current_worker_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    open_jobs = Job.query.filter(
    Job.status.in_(["POSTED", "MATCHING", "APPLICANTS"]),
    Job.job_date >= date.today()).all()

    recommendations = []
    for job in open_jobs:
        ranked = rank_workers_for_job(job, [profile], Config.MATCHING_WEIGHTS_PATH)
        if ranked:
            entry = ranked[0]
            job_dict = job.to_dict()
            job_dict["match_score"] = entry["match_score"]
            job_dict["breakdown"] = entry["breakdown"]
            job_dict["reasons"] = entry["reasons"]
            recommendations.append(job_dict)

    recommendations.sort(key=lambda j: j["match_score"], reverse=True)
    return jsonify({"jobs": recommendations}), 200


@worker_bp.route("/applications", methods=["GET"])
@role_required("worker")
def my_applications():
    """Optional query param: ?status=PENDING|SELECTED|... to filter."""
    try:
        profile = _get_current_worker_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    query = JobApplication.query.filter_by(worker_id=profile.id)
    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter_by(status=status_filter.upper())

    applications = query.order_by(JobApplication.applied_at.desc()).all()
    result = []
    for app in applications:
        d = app.to_dict()
        d["job"] = app.job.to_dict()
        result.append(d)
    return jsonify({"applications": result}), 200


@worker_bp.route("/dashboard-stats", methods=["GET"])
@role_required("worker")
def dashboard_stats():
    try:
        profile = _get_current_worker_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    accepted = JobApplication.query.filter_by(worker_id=profile.id, status="SELECTED").count()
    completed = JobApplication.query.filter_by(worker_id=profile.id, status="COMPLETED").count()
    available_jobs_count = Job.query.filter(
        Job.status.in_(["POSTED", "MATCHING", "APPLICANTS"]), Job.job_date >= date.today()
    ).count()

    return jsonify({
        "available_jobs": available_jobs_count,
        "accepted_jobs": accepted,
        "completed_jobs": completed,
        "average_rating": round(profile.average_rating, 2),
        "reliability_score": round(profile.reliability_score, 3),
    }), 200
