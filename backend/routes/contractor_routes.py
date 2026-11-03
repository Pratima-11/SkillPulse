"""
Contractor-facing endpoints.

GET  /api/contractor/profile
PUT  /api/contractor/profile
POST /api/contractor/jobs
GET  /api/contractor/jobs
GET  /api/contractor/jobs/<id>/recommended-workers
POST /api/contractor/applications/<id>/select
POST /api/contractor/applications/<id>/reject
POST /api/contractor/jobs/<id>/status
POST /api/contractor/applications/<id>/rate
GET  /api/contractor/dashboard-stats
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.config import Config
from models.contractor_profile import ContractorProfile
from models.job import Job, VALID_TRANSITIONS
from models.job_application import JobApplication
from models.worker_profile import WorkerProfile
from models.availability import Availability
from models.skill import Skill
from models.rating import Rating
from models.notification import Notification
from utils.decorators import role_required
from utils.validators import (
    ValidationError, validate_positive_number, validate_latitude,
    validate_longitude, validate_date_not_past, validate_rating_value, require_fields,
)
from services.reliability_service import update_worker_reliability
from models.replacement_invitation import ReplacementInvitation
from services.matching_service import rank_workers_for_job, get_job_vacancies
from services.wage_advisor_service import get_wage_recommendation

contractor_bp = Blueprint("contractor", __name__, url_prefix="/api/contractor")


def _get_current_contractor_profile():
    user_id = get_jwt_identity()
    profile = ContractorProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        raise ValidationError("Contractor profile not found for this account.")
    return profile


@contractor_bp.route("/profile", methods=["GET"])
@role_required("contractor")
def get_profile():
    try:
        profile = _get_current_contractor_profile()
        return jsonify({"profile": profile.to_dict()}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404


@contractor_bp.route("/profile", methods=["PUT"])
@role_required("contractor")
def update_profile():
    data = request.get_json(silent=True) or {}
    try:
        profile = _get_current_contractor_profile()
        for field in ("company_name", "contact_person", "phone", "area_text"):
            if field in data:
                setattr(profile, field, data[field])
        if "latitude" in data:
            profile.latitude = validate_latitude(data["latitude"])
        if "longitude" in data:
            profile.longitude = validate_longitude(data["longitude"])

        db.session.commit()
        return jsonify({"profile": profile.to_dict()}), 200
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@contractor_bp.route("/jobs", methods=["POST"])
@role_required("contractor")
def create_job():
    """
    Request body:
    {
      "skill_name": "Painter", "workers_required": 2, "job_date": "2026-09-27",
      "latitude": 12.97, "longitude": 77.59, "area_text": "Koramangala",
      "wage": 800, "working_hours": "9am-5pm", "min_experience": 1,
      "description": "Interior wall painting"
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        require_fields(data, ["skill_name", "job_date", "latitude", "longitude", "wage"])
        profile = _get_current_contractor_profile()

        skill_name = str(data["skill_name"]).strip()
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.session.add(skill)
            db.session.flush()

        job_date = validate_date_not_past(data["job_date"], "job_date")
        wage = validate_positive_number(data["wage"], "wage")
        lat = validate_latitude(data["latitude"])
        lng = validate_longitude(data["longitude"])
        workers_required = int(data.get("workers_required", 1))
        min_experience = validate_positive_number(data.get("min_experience", 0), "min_experience")

        job = Job(
            contractor_id=profile.id,
            skill_id=skill.id,
            workers_required=workers_required,
            job_date=job_date,
            latitude=lat,
            longitude=lng,
            area_text=data.get("area_text"),
            wage=wage,
            working_hours=data.get("working_hours"),
            min_experience=min_experience,
            description=data.get("description"),
            status="POSTED",
        )
        db.session.add(job)
        db.session.commit()
        return jsonify({"job": job.to_dict()}), 201
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@contractor_bp.route("/jobs", methods=["GET"])
@role_required("contractor")
def list_my_jobs():
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    status_filter = request.args.get("status")
    query = Job.query.filter_by(contractor_id=profile.id)
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200

@contractor_bp.route("/jobs/<int:job_id>/applications", methods=["GET"])
@role_required("contractor")
def job_applications(job_id):
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    job = Job.query.filter_by(
        id=job_id,
        contractor_id=profile.id
    ).first()

    if not job:
        return jsonify({"error": "Job not found or does not belong to you."}), 404

    applications = JobApplication.query.filter_by(
        job_id=job.id
    ).order_by(JobApplication.applied_at.desc()).all()

    result = []

    for application in applications:
        worker = application.worker.to_dict()

        availability = Availability.query.filter_by(
            worker_id=application.worker_id,
            available_date=job.job_date,
        ).first()

        worker["available_for_job_date"] = (
            availability.is_available if availability else False
        )

        print(
            "DEBUG AVAILABILITY:",
            application.worker_id,
            job.job_date,
            availability.is_available if availability else "NO RECORD"
        )
        worker["application_id"] = application.id
        worker["application_status"] = application.status
        worker["has_rating"] = application.rating is not None
        worker["match_score"] = application.match_score
        worker["score_breakdown"] = application.score_breakdown
        worker["applied_at"] = (
            application.applied_at.isoformat()
            if application.applied_at
            else None
        )

        result.append(worker)

    return jsonify({
        "applications": result
    }), 200

@contractor_bp.route("/jobs/<int:job_id>/recommended-workers", methods=["GET"])
@role_required("contractor")
def recommended_workers(job_id):
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    job = Job.query.filter_by(id=job_id, contractor_id=profile.id).first()
    if not job:
        return jsonify({"error": "Job not found or does not belong to you."}), 404

    candidate_workers = WorkerProfile.query.filter_by(verification_status="verified").all()
    if not candidate_workers:
        # Fall back to all workers if none are verified yet (keeps demo usable)
        candidate_workers = WorkerProfile.query.all()

    ranked = rank_workers_for_job(job, candidate_workers, Config.MATCHING_WEIGHTS_PATH)

    result = []
    for entry in ranked:
        worker_dict = entry["worker"].to_dict()
        worker_dict["match_score"] = entry["match_score"]
        worker_dict["breakdown"] = entry["breakdown"]
        worker_dict["reasons"] = entry["reasons"]
        result.append(worker_dict)

    if job.status == "POSTED":
        job.status = "MATCHING"
        db.session.commit()

    return jsonify({"workers": result}), 200


@contractor_bp.route("/applications/<int:application_id>/select", methods=["POST"])
@role_required("contractor")
def select_worker(application_id):

    from sqlalchemy import select

    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    application = JobApplication.query.get(application_id)

    if not application or application.job.contractor_id != profile.id:
        return jsonify({"error": "Application not found."}), 404

    try:
        job = db.session.execute(
            select(Job)
            .where(Job.id == application.job_id)
            .with_for_update()
        ).scalar_one_or_none()

        if not job or job.contractor_id != profile.id:
            db.session.rollback()
            return jsonify({"error": "Job not found."}), 404

        db.session.refresh(application)

        if application.status != "PENDING":
            db.session.rollback()
            return jsonify({
                "error": f"Cannot select an application in status {application.status}."
            }), 400

        selected_count = JobApplication.query.filter_by(
            job_id=job.id,
            status="SELECTED",
        ).count()

        if selected_count >= job.workers_required:
            db.session.rollback()
            return jsonify({
                "error": "This job has already reached its worker requirement."
            }), 400

        application.status = "SELECTED"
        application.worker.jobs_accepted += 1

        if job.status == "MATCHING":
            job.status = "APPLICANTS"

        if job.can_transition_to("WORKER_SELECTED"):
            job.status = "WORKER_SELECTED"

        db.session.add(Notification(
            user_id=application.worker.user_id,
            message=f"You have been selected for job #{job.id}.",
            notif_type="SELECTED",
        ))

        db.session.commit()

        return jsonify({
            "application": application.to_dict()
        }), 200

    except Exception:
        db.session.rollback()
        raise

@contractor_bp.route(
    "/applications/<int:application_id>/report-unavailable",
    methods=["POST"],
)
@role_required("contractor")
def report_selected_worker_unavailable(application_id):
    """Release a selected worker position so the contractor can find a replacement."""
    from sqlalchemy import select

    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    application = JobApplication.query.get(application_id)
    if not application or application.job.contractor_id != profile.id:
        return jsonify({"error": "Application not found."}), 404

    try:
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id).with_for_update()
        ).scalar_one_or_none()

        if not job or job.contractor_id != profile.id:
            db.session.rollback()
            return jsonify({"error": "Job not found."}), 404

        db.session.refresh(application)

        if application.status != "SELECTED":
            db.session.rollback()
            return jsonify({
                "error": "Only a currently selected worker can be reported unavailable."
            }), 400

        if job.status not in ("MATCHING", "APPLICANTS", "WORKER_SELECTED", "CONFIRMED", "IN_PROGRESS"):
            db.session.rollback()
            return jsonify({"error": "This job is not eligible for emergency replacement."}), 409

        application.status = "CANCELLED"
        application.worker.jobs_cancelled = (application.worker.jobs_cancelled or 0) + 1
        update_worker_reliability(application.worker)

        db.session.add(Notification(
            user_id=application.worker.user_id,
            message=f"You were marked unavailable for job #{job.id}. The contractor will look for a replacement.",
            notif_type="CANCELLED",
        ))

        db.session.commit()
        return jsonify({
            "message": "Worker position released. You can now find a replacement.",
            "application": application.to_dict(),
            "vacancies": get_job_vacancies(job),
        }), 200
    except Exception:
        db.session.rollback()
        raise


@contractor_bp.route(
    "/jobs/<int:job_id>/replacement-candidates",
    methods=["GET"],
)
@role_required("contractor")
def replacement_candidates(job_id):
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    job = Job.query.filter_by(
        id=job_id,
        contractor_id=profile.id,
    ).first()

    if not job:
        return jsonify({"error": "Job not found or does not belong to you."}), 404

    vacancies = get_job_vacancies(job)

    if vacancies == 0:
        return jsonify({
            "job_id": job.id,
            "vacancies": 0,
            "workers": [],
            "message": "No replacement vacancies are available.",
        }), 200

    if job.status not in (
        "MATCHING",
        "APPLICANTS",
        "WORKER_SELECTED",
        "CONFIRMED",
        "IN_PROGRESS",
    ):
        return jsonify({
            "job_id": job.id,
            "vacancies": vacancies,
            "workers": [],
            "message": "This job is not currently eligible for replacement matching.",
        }), 200

    candidate_workers = WorkerProfile.query.filter_by(
        verification_status="verified",
    ).all()

    ranked = rank_workers_for_job(
        job,
        candidate_workers,
        Config.MATCHING_WEIGHTS_PATH,
    )

    selected_worker_ids = {
        application.worker_id
        for application in JobApplication.query.filter_by(
            job_id=job.id,
            status="SELECTED",
        ).all()
    }

    result = []

    for entry in ranked:
        worker = entry["worker"]

        if worker.id in selected_worker_ids:
            continue

        worker_dict = worker.to_dict()
        worker_dict["match_score"] = entry["match_score"]
        worker_dict["breakdown"] = entry["breakdown"]
        worker_dict["reasons"] = entry["reasons"]
        result.append(worker_dict)

    return jsonify({
        "job_id": job.id,
        "vacancies": vacancies,
        "workers": result,
    }), 200


@contractor_bp.route(
    "/jobs/<int:job_id>/replacement-invitations",
    methods=["POST"],
)
@role_required("contractor")
def invite_replacement_worker(job_id):
    data = request.get_json(silent=True) or {}

    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    worker_id = data.get("worker_id")
    if not isinstance(worker_id, int) or isinstance(worker_id, bool):
        return jsonify({"error": "A valid worker_id is required."}), 400

    job = Job.query.filter_by(
        id=job_id,
        contractor_id=profile.id,
    ).first()

    if not job:
        return jsonify({"error": "Job not found or does not belong to you."}), 404

    vacancies = get_job_vacancies(job)
    if vacancies <= 0:
        return jsonify({"error": "No replacement vacancies are available."}), 409

    if job.status not in (
        "MATCHING",
        "APPLICANTS",
        "WORKER_SELECTED",
        "CONFIRMED",
        "IN_PROGRESS",
    ):
        return jsonify({"error": "This job is not eligible for replacement invitations."}), 409

    worker = WorkerProfile.query.filter_by(
        id=worker_id,
        verification_status="verified",
    ).first()

    if not worker:
        return jsonify({"error": "Verified worker not found."}), 404

    # Only invite workers returned by the existing eligibility matcher.
    ranked = rank_workers_for_job(
        job,
        [worker],
        Config.MATCHING_WEIGHTS_PATH,
    )

    if not ranked:
        return jsonify({
            "error": "This worker does not meet the job's matching requirements."
        }), 400

    existing_application = JobApplication.query.filter_by(
        job_id=job.id,
        worker_id=worker.id,
    ).first()

    if existing_application and existing_application.status != "PENDING":
        return jsonify({
            "error": f"This worker already has an application in status {existing_application.status}."
        }), 409

    existing_invitation = ReplacementInvitation.query.filter(
        ReplacementInvitation.job_id == job.id,
        ReplacementInvitation.worker_id == worker.id,
        ReplacementInvitation.status.in_(["PENDING", "ACCEPTED"]),
    ).first()

    if existing_invitation:
        return jsonify({"error": "An active invitation already exists."}), 409

    entry = ranked[0]
    invitation = ReplacementInvitation(
    job_id=job.id,
    worker_id=worker.id,
    contractor_id=profile.id,
    status="PENDING",
    match_score=entry["match_score"],
    score_breakdown=entry["breakdown"],
    expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
)

    db.session.add(invitation)
    db.session.add(Notification(
        user_id=worker.user_id,
        message=f"You have been invited as a replacement for job #{job.id}.",
        notif_type="REPLACEMENT_INVITATION",
    ))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to create invitation. Please retry."}), 409

    return jsonify({"invitation": invitation.to_dict()}), 201




@contractor_bp.route("/applications/<int:application_id>/reject", methods=["POST"])
@role_required("contractor")
def reject_worker(application_id):
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    application = JobApplication.query.get(application_id)
    if not application or application.job.contractor_id != profile.id:
        return jsonify({"error": "Application not found."}), 404

    if application.status not in ("PENDING", "SELECTED"):
        return jsonify({"error": f"Cannot reject an application in status {application.status}."}), 400

    application.status = "REJECTED"
    db.session.add(Notification(
        user_id=application.worker.user_id,
        message=f"Your application for job #{application.job_id} was not selected.",
        notif_type="REJECTED",
    ))
    db.session.commit()
    return jsonify({"application": application.to_dict()}), 200



@contractor_bp.route("/jobs/<int:job_id>/status", methods=["POST"])
@role_required("contractor")
def update_job_status(job_id):
    """
    Request body: { "status": "CONFIRMED" }
    Enforces the job lifecycle - invalid transitions are rejected (Section 16).
    """
    data = request.get_json(silent=True) or {}
    new_status = str(data.get("status", "")).upper()

    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    job = Job.query.filter_by(
        id=job_id,
        contractor_id=profile.id
    ).first()

    if not job:
        return jsonify({"error": "Job not found."}), 404

    if new_status not in VALID_TRANSITIONS:
        return jsonify({"error": f"Unknown status: {new_status}"}), 400

    if not job.can_transition_to(new_status):
        return jsonify({
            "error": f"Cannot move job from {job.status} to {new_status}."
        }), 400

    job.status = new_status

    if new_status == "COMPLETED":
        selected_apps = JobApplication.query.filter_by(
            job_id=job.id,
            status="SELECTED"
        ).all()

        for app in selected_apps:
            app.status = "COMPLETED"
            app.worker.jobs_completed += 1
            update_worker_reliability(app.worker)

        # No replacement invitations should remain pending
        # once the job has been completed.
        pending_invitations = ReplacementInvitation.query.filter_by(
            job_id=job.id,
            status="PENDING"
        ).all()

        for invitation in pending_invitations:
            invitation.status = "CANCELLED"
            invitation.responded_at = datetime.now(timezone.utc)

    elif new_status == "CANCELLED":
        active_apps = JobApplication.query.filter(
            JobApplication.job_id == job.id,
            JobApplication.status.in_(["PENDING", "SELECTED"]),
        ).all()

        for app in active_apps:
            if app.status == "SELECTED":
                app.worker.jobs_cancelled += 1
                update_worker_reliability(app.worker)

            app.status = "CANCELLED"

        # Cancel pending replacement invitations for this job.
        pending_invitations = ReplacementInvitation.query.filter_by(
            job_id=job.id,
            status="PENDING"
        ).all()

        for invitation in pending_invitations:
            invitation.status = "CANCELLED"
            invitation.responded_at = datetime.now(timezone.utc)

    db.session.commit()
    return jsonify({"job": job.to_dict()}), 200


@contractor_bp.route("/applications/<int:application_id>/rate", methods=["POST"])
@role_required("contractor")
def rate_worker(application_id):
    """
    Request body: { "rating_value": 5, "comment": "Great work" }
    Only allowed once a job_application has reached COMPLETED.
    """
    data = request.get_json(silent=True) or {}
    try:
        profile = _get_current_contractor_profile()
        require_fields(data, ["rating_value"])
        rating_value = validate_rating_value(data["rating_value"])

        application = JobApplication.query.get(application_id)
        if not application or application.job.contractor_id != profile.id:
            raise ValidationError("Application not found.")
        if application.status != "COMPLETED":
            raise ValidationError("Can only rate applications that are COMPLETED.")
        if application.rating:
            raise ValidationError("This application has already been rated.")

        rating = Rating(
            job_application_id=application.id,
            rating_value=rating_value,
            comment=data.get("comment"),
        )
        db.session.add(rating)

        worker = application.worker
        all_ratings = [
            r.rating_value for r in Rating.query.join(JobApplication).filter(
                JobApplication.worker_id == worker.id
            ).all()
        ] + [rating_value]
        worker.average_rating = sum(all_ratings) / len(all_ratings)
        update_worker_reliability(worker)

        db.session.add(Notification(
            user_id=worker.user_id,
            message=f"You received a {rating_value}-star rating for job #{application.job_id}.",
            notif_type="RATING_RECEIVED",
        ))

        db.session.commit()
        return jsonify({"rating": rating.to_dict()}), 201
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@contractor_bp.route("/dashboard-stats", methods=["GET"])
@role_required("contractor")
def dashboard_stats():
    try:
        profile = _get_current_contractor_profile()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 404

    posted = Job.query.filter_by(contractor_id=profile.id).count()
    open_jobs = Job.query.filter(
        Job.contractor_id == profile.id,
        Job.status.in_(["POSTED", "MATCHING", "APPLICANTS", "WORKER_SELECTED", "CONFIRMED", "IN_PROGRESS"]),
    ).count()
    completed = Job.query.filter_by(contractor_id=profile.id, status="COMPLETED").count()
    workers_selected = JobApplication.query.join(Job).filter(
        Job.contractor_id == profile.id, JobApplication.status.in_(["SELECTED", "COMPLETED"])
    ).count()

    return jsonify({
        "posted_jobs": posted,
        "open_jobs": open_jobs,
        "completed_jobs": completed,
        "workers_selected": workers_selected,
    }), 200




@contractor_bp.route("/wage-advisor", methods=["POST"])
@role_required("contractor")
def contractor_wage_advisor():
    data = request.get_json(silent=True) or {}

    result = get_wage_recommendation(
        skill_name=data.get("skill_name"),
        area_text=data.get("area_text"),
        experience_years=data.get("experience_years"),
        working_hours=data.get("working_hours"),
        offered_wage=data.get("offered_wage"),
    )

    if not result.get("success"):
        error_message = result.get("error", "Unable to estimate wages.")
        status_code = (
            404 if error_message.endswith("was not found.")
            else 400
        )
        return jsonify(result), status_code

    return jsonify(result), 200
