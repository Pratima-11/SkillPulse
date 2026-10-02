"""
worker_profiles table.

Holds everything specific to a worker account: location (for the Haversine
distance calculation), wage expectation, experience, verification status,
and the reliability score that the matching engine consumes.
"""

from datetime import datetime, timezone
from app.extensions import db
from models.skill import worker_skills


class WorkerProfile(db.Model):
    __tablename__ = "worker_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # Location - required for Haversine distance calculation.
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    area_text = db.Column(db.String(200), nullable=True)

    expected_wage = db.Column(db.Float, nullable=False, default=0)
    experience_years = db.Column(db.Float, nullable=False, default=0)

    verification_status = db.Column(
        db.Enum("pending", "verified", "rejected", name="verification_status"),
        default="pending",
        nullable=False,
    )
    verification_document_path = db.Column(db.String(255), nullable=True)

    # Reliability score (0-1). Recomputed after every completed job.
    # In Phase 4 this is produced by the ML model; until then it defaults
    # to a neutral score computed by services/reliability_service.py.
    reliability_score = db.Column(db.Float, default=0.5, nullable=False)

    jobs_completed = db.Column(db.Integer, default=0, nullable=False)
    jobs_accepted = db.Column(db.Integer, default=0, nullable=False)
    jobs_cancelled = db.Column(db.Integer, default=0, nullable=False)
    average_rating = db.Column(db.Float, default=0.0, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    skills = db.relationship("Skill", secondary=worker_skills, backref="workers")
    availability_entries = db.relationship(
        "Availability", backref="worker", cascade="all, delete-orphan", lazy="dynamic"
    )
    applications = db.relationship(
        "JobApplication", backref="worker", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_skills=True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "phone": self.phone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "area_text": self.area_text,
            "expected_wage": self.expected_wage,
            "experience_years": self.experience_years,
            "verification_status": self.verification_status,
            "reliability_score": round(self.reliability_score, 3),
            "jobs_completed": self.jobs_completed,
            "jobs_accepted": self.jobs_accepted,
            "jobs_cancelled": self.jobs_cancelled,
            "average_rating": round(self.average_rating, 2),
        }
        if include_skills:
            data["skills"] = [s.name for s in self.skills]
        return data
