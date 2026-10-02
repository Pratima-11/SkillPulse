from datetime import date
from flask import Blueprint, jsonify
from app.extensions import db
from models.user import User
from models.worker_profile import WorkerProfile
from models.contractor_profile import ContractorProfile
from models.job import Job
from models.rating import Rating

public_bp = Blueprint("public", __name__, url_prefix="/api/public")

@public_bp.route("/stats", methods=["GET"])
def stats():
    completed_jobs = Job.query.filter_by(status="COMPLETED").count()
    workers = WorkerProfile.query.filter_by(verification_status="verified").count()
    contractors = ContractorProfile.query.count()
    ratings = [r.rating_value for r in Rating.query.all()]
    avg_rating = round(sum(ratings)/len(ratings), 1) if ratings else None
    return jsonify({
        "verified_workers": workers,
        "contractors": contractors,
        "jobs_completed": completed_jobs,
        "average_rating": avg_rating,
        "open_jobs": Job.query.filter(Job.status.in_(["POSTED","MATCHING","APPLICANTS"]), Job.job_date >= date.today()).count(),
    }), 200
