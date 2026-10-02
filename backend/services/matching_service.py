"""
Matching / ranking engine - the core research contribution of SkillPulse.

Combines skill compatibility, location, next-day availability, experience,
wage compatibility, and reliability into a single transparent, weighted
suitability score. Weights are loaded from config/matching_weights.json,
never hard-coded, so they can be tuned without touching this logic.

Skill match and availability are treated as HARD FILTERS: a worker missing
the required skill, or unavailable on the job date, is excluded from the
ranked list entirely rather than merely penalised. This mirrors how the
real-world naka process works - you would never send an unavailable
plumber to a masonry job just because he lives nearby.
"""

import json
from models.worker_profile import WorkerProfile
from models.availability import Availability
from models.job_application import JobApplication
from services.distance_service import haversine_distance_km, location_score

_weights_cache = None


def _load_weights(weights_path: str) -> dict:
    global _weights_cache
    if _weights_cache is None:
        with open(weights_path, "r") as f:
            _weights_cache = json.load(f)
    return _weights_cache


def _experience_score(worker_experience: float, required_experience: float) -> float:
    if required_experience <= 0:
        return 1.0
    return max(0.0, min(worker_experience / required_experience, 1.0))


def _wage_score(expected_wage: float, offered_wage: float, tolerance_ratio: float) -> float:
    if expected_wage <= offered_wage:
        return 1.0
    if offered_wage <= 0:
        return 0.0
    excess_ratio = (expected_wage - offered_wage) / offered_wage
    if excess_ratio >= tolerance_ratio:
        return 0.0
    return 1.0 - (excess_ratio / tolerance_ratio)


def _get_reliability_score(worker: WorkerProfile) -> float:
    """
    Tries the ML model first (Phase 4); falls back to the rule-based
    calculation if the trained model file does not exist yet, so this
    function works correctly in every phase of the project.
    """
    try:
        from ml.predict import predict_reliability
        features = {
            "jobs_completed": worker.jobs_completed,
            "jobs_accepted": worker.jobs_accepted,
            "jobs_cancelled": worker.jobs_cancelled,
            "average_rating": worker.average_rating,
            "experience_years": worker.experience_years,
        }
        return predict_reliability(features)
    except Exception:
        from services.reliability_service import compute_rule_based_reliability
        return compute_rule_based_reliability(worker)


def rank_workers_for_job(job, candidate_workers, weights_path: str):
    """
    job: models.job.Job instance
    candidate_workers: iterable of WorkerProfile instances to evaluate
    weights_path: path to matching_weights.json (from app config)

    Returns a list of dicts, sorted by match_score descending:
        [{ "worker": WorkerProfile, "match_score": float,
           "breakdown": {...}, "reasons": [...] }, ...]

    Workers who fail the hard filters (skill / availability / out of
    radius) are excluded from the returned list entirely.
    """
    config = _load_weights(weights_path)
    weights = config["weights"]
    max_radius_km = config.get("max_radius_km", 10)
    wage_tolerance_ratio = config.get("wage_tolerance_ratio", 0.2)

    required_skill_id = job.skill_id
    results = []

    for worker in candidate_workers:
        reasons = []

        # --- HARD FILTER 1: skill match ---
        worker_skill_ids = {s.id for s in worker.skills}
        if required_skill_id not in worker_skill_ids:
            continue

        # --- HARD FILTER 2: availability on job date ---
        availability_row = Availability.query.filter_by(
            worker_id=worker.id, available_date=job.job_date
        ).first()
        if not availability_row or not availability_row.is_available:
            continue
        reasons.append("Worker is available on the required date")

        # --- HARD FILTER 3: prevent double-booking on the same date ---
        conflicting = JobApplication.query.join(JobApplication.job).filter(
            JobApplication.worker_id == worker.id,
            JobApplication.status.in_(["SELECTED", "CONFIRMED", "COMPLETED"]),
            JobApplication.job.has(job_date=job.job_date),
        ).first()
        if conflicting:
            continue

        # --- HARD FILTER 4: location radius ---
        if worker.latitude is None or worker.longitude is None:
            continue
        distance_km = haversine_distance_km(
            worker.latitude, worker.longitude, job.latitude, job.longitude
        )
        if distance_km > max_radius_km:
            continue

        loc_score = location_score(distance_km, max_radius_km)
        if loc_score > 0.5:
            reasons.append(f"Job is within preferred distance ({distance_km:.1f} km away)")
        else:
            reasons.append(f"Job is within allowed radius ({distance_km:.1f} km away)")

        # --- Soft factors ---
        exp_score = _experience_score(worker.experience_years, job.min_experience)
        if exp_score >= 1.0:
            reasons.append("Experience requirement is satisfied")

        wage_score = _wage_score(worker.expected_wage, job.wage, wage_tolerance_ratio)
        if wage_score >= 1.0:
            reasons.append("Wage is compatible")

        reliability_score = _get_reliability_score(worker)
        if reliability_score >= 0.7:
            reasons.append("Good reliability score")

        reasons.insert(0, "Required skill matches")

        overall_score = (
            loc_score * weights["location"]
            + exp_score * weights["experience"]
            + wage_score * weights["wage"]
            + reliability_score * weights["reliability"]
        )

        results.append({
            "worker": worker,
            "match_score": round(overall_score * 100, 2),  # expressed as a percentage
            "breakdown": {
                "location_score": round(loc_score, 3),
                "experience_score": round(exp_score, 3),
                "wage_score": round(wage_score, 3),
                "reliability_score": round(reliability_score, 3),
                "distance_km": round(distance_km, 2),
            },
            "reasons": reasons,
        })

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results
