"""
Reliability scoring service.

For Phase 2/3 (before the ML model exists) this computes reliability with
a transparent rule-based formula, so the backend is fully runnable on its
own. In Phase 4, matching_service.py will try to load a trained ML model
(ml/predict.py) and prefer its prediction; if the model file is not found
it falls back to this same rule-based function - so the system never
breaks if the ML step hasn't been run yet.
"""

from models.worker_profile import WorkerProfile


def compute_rule_based_reliability(worker: WorkerProfile) -> float:
    """
    Reliability = weighted combination of completion rate and rating,
    with a small experience bonus. Returns a value in [0, 1].

    A brand-new worker with no job history gets a neutral 0.5 score
    (neither penalised nor favoured) rather than 0, so new workers are
    not unfairly excluded from their first few matches.
    """
    total_jobs = worker.jobs_accepted
    if total_jobs == 0:
        return 0.5

    completion_rate = worker.jobs_completed / total_jobs if total_jobs > 0 else 0
    cancellation_penalty = worker.jobs_cancelled / total_jobs if total_jobs > 0 else 0
    normalized_rating = (worker.average_rating / 5.0) if worker.average_rating else 0.5

    score = (
        (completion_rate * 0.5)
        + (normalized_rating * 0.4)
        - (cancellation_penalty * 0.3)
    )
    # small bump for experience, capped
    experience_bonus = min(worker.experience_years / 20.0, 0.1)
    score += experience_bonus

    return max(0.0, min(1.0, score))


def update_worker_reliability(worker: WorkerProfile) -> None:
    """Recomputes and persists worker.reliability_score. Caller must commit."""
    worker.reliability_score = compute_rule_based_reliability(worker)
