
"""
Smart Wage Advisor for SkillPulse.

Estimates a daily wage range using historical contractor job offers
for the requested skill and location.

Job.wage represents an offered wage, not a verified payment.
WorkerProfile.expected_wage represents a worker's expectation.
Recommendations are estimates, not guaranteed market rates.
"""

import math
from statistics import median

from sqlalchemy import func

from models.job import Job
from models.worker_profile import WorkerProfile
from models.skill import Skill


MIN_COMPARABLE_JOBS = 3
MIN_COMPARABLE_WORKERS = 3


def _normalise_text(value):
    """Normalize text for case-insensitive location comparison."""
    return " ".join(str(value or "").strip().lower().split())


def _valid_positive_number(value):
    """Return a positive finite float, or None for invalid values."""
    try:
        number = float(value)
        if number > 0 and math.isfinite(number):
            return number
    except (TypeError, ValueError):
        pass

    return None


def _build_range(values):
    """Build a minimum, median, and maximum wage range."""
    valid_values = sorted(
        number
        for value in values
        if (number := _valid_positive_number(value)) is not None
    )

    if not valid_values:
        return None

    return {
        "minimum": round(valid_values[0], 2),
        "median": round(median(valid_values), 2),
        "maximum": round(valid_values[-1], 2),
    }


def _classify_wage(offered_wage, wage_range):
    """Compare a contractor's offered wage with the suggested range."""
    if not wage_range:
        return "insufficient_data"

    if offered_wage < wage_range["minimum"]:
        return "below_range"

    if offered_wage > wage_range["maximum"]:
        return "above_range"

    return "within_range"


def get_wage_recommendation(
    skill_name,
    area_text=None,
    experience_years=None,
    working_hours=None,
    offered_wage=None,
):
    """
    Recommend a daily wage range using available SkillPulse records.

    Historical job offers are preferred. Worker wage expectations are
    used as a separate fallback when there are too few comparable jobs.
    """
    if not isinstance(skill_name, str) or not skill_name.strip():
        return {
            "success": False,
            "error": "skill_name is required.",
        }

    if experience_years is not None:
        try:
            experience_years = float(experience_years)
        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "experience_years must be between 0 and 80.",
            }

        if (
            not math.isfinite(experience_years)
            or experience_years < 0
            or experience_years > 80
        ):
            return {
                "success": False,
                "error": "experience_years must be between 0 and 80.",
            }

    if offered_wage is not None:
        offered_wage = _valid_positive_number(offered_wage)

        if offered_wage is None:
            return {
                "success": False,
                "error": "offered_wage must be a positive number.",
            }

    skill = Skill.query.filter(
        func.lower(Skill.name) == skill_name.strip().lower()
    ).first()

    if not skill:
        return {
            "success": False,
            "error": f"Skill '{skill_name.strip()}' was not found.",
        }

    jobs = Job.query.filter(
        Job.skill_id == skill.id,
        Job.wage > 0,
        Job.status != "CANCELLED",
    ).all()

    requested_area = _normalise_text(area_text)

    area_jobs = [
        job
        for job in jobs
        if requested_area
        and _normalise_text(job.area_text) == requested_area
    ]

    reference_jobs = area_jobs
    location_scope = "same_area"

    job_wages = [
        wage
        for job in reference_jobs
        if (wage := _valid_positive_number(job.wage)) is not None
    ]

    job_range = _build_range(job_wages)

    workers = WorkerProfile.query.filter(
        WorkerProfile.expected_wage > 0
    ).all()

    expected_wages = []

    for worker in workers:
        has_skill = any(
            worker_skill.id == skill.id
            for worker_skill in worker.skills
        )

        if not has_skill:
            continue

        if (
            requested_area
            and _normalise_text(worker.area_text) != requested_area
        ):
            continue

        wage = _valid_positive_number(worker.expected_wage)

        if wage is not None:
            expected_wages.append(wage)

    expectation_range = _build_range(expected_wages)

    enough_job_data = len(job_wages) >= MIN_COMPARABLE_JOBS
    enough_worker_data = (
        len(expected_wages) >= MIN_COMPARABLE_WORKERS
    )

    if enough_job_data:
        recommended_range = job_range
        basis = "historical_job_offers"
        confidence = (
            "moderate" if len(job_wages) >= 10 else "limited"
        )
        explanation = (
            "Estimated from historical job offers for this skill. "
            "These records show offered wages, not confirmed payments."
        )

    elif enough_worker_data:
        recommended_range = expectation_range
        basis = "worker_expectations"
        confidence = "limited"
        explanation = (
            "There are too few comparable job offers. This range uses "
            "worker wage expectations as a separate fallback reference, "
            "not as verified market wages."
        )

    else:
        recommended_range = None
        basis = "insufficient_data"
        confidence = "insufficient"
        explanation = (
            "There are not enough comparable job offers or worker "
            "expectations to provide a reliable wage range."
        )

    offered_wage_classification = (
        _classify_wage(offered_wage, recommended_range)
        if offered_wage is not None
        else None
    )

    reasons = [
        f"Required skill: {skill.name}.",
        f"Location scope: {location_scope.replace('_', ' ')}.",
    ]

    if experience_years is not None:
        reasons.append(
            "Experience was provided, but the recommendation is not "
            "adjusted for experience because its wage effect has not "
            "been reliably established in the available records."
        )

    if working_hours:
        reasons.append(
            "The available records are not normalized by working hours."
        )

    return {
        "success": True,
        "skill": skill.name,
        "location": area_text,
        "experience_years": experience_years,
        "working_hours": working_hours,
        "offered_wage": offered_wage,
        "recommended_range": recommended_range,
        "offered_wage_classification": offered_wage_classification,
        "basis": basis,
        "confidence": confidence,
        "data": {
            "comparable_job_offers_count": len(job_wages),
            "worker_expectations_count": len(expected_wages),
            "historical_offer_range": job_range,
            "worker_expectation_range": expectation_range,
        },
        "explanation": explanation,
        "reasons": reasons,
        "disclaimer": (
            "Estimates are based on available SkillPulse records. "
            "Offered wages and worker expectations are not proof of "
            "wages actually paid. This feature does not guarantee "
            "prevailing market rates."
        ),
    }
