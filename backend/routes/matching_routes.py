"""
Direct access to the matching engine, independent of the job/worker
workflow. This exists specifically to satisfy Section 28 of the project
spec: a reproducible test case proving the matching logic works, callable
as a plain API request (and reused by the automated tests in Phase 5).

GET /api/matching/job/<job_id>  - full ranked list for an existing job
                                   (any authenticated role may call this
                                   for transparency/demo purposes)
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.config import Config
from models.job import Job
from models.worker_profile import WorkerProfile
from services.matching_service import rank_workers_for_job

matching_bp = Blueprint("matching", __name__, url_prefix="/api/matching")


@matching_bp.route("/job/<int:job_id>", methods=["GET"])
@jwt_required()
def matching_for_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404

    all_workers = WorkerProfile.query.all()
    ranked = rank_workers_for_job(job, all_workers, Config.MATCHING_WEIGHTS_PATH)

    result = []
    for entry in ranked:
        result.append({
            "worker_id": entry["worker"].id,
            "worker_name": entry["worker"].full_name,
            "match_score": entry["match_score"],
            "breakdown": entry["breakdown"],
            "reasons": entry["reasons"],
        })

    return jsonify({
        "job": job.to_dict(),
        "ranked_workers": result,
        "excluded_note": "Workers missing the required skill, unavailable on "
                          "the job date, or outside the configured radius are "
                          "excluded entirely and will not appear above.",
    }), 200
