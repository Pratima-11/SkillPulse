"""
jobs table.

Represents one labour requirement posted by a contractor for a specific
(usually next) date. Status follows the lifecycle defined in Phase 1:

POSTED -> MATCHING -> APPLICANTS -> WORKER_SELECTED -> CONFIRMED
       -> IN_PROGRESS -> COMPLETED   (or CANCELLED at any point before COMPLETED)
"""

from datetime import datetime, timezone
from app.extensions import db

JOB_STATUSES = (
    "POSTED",
    "MATCHING",
    "APPLICANTS",
    "WORKER_SELECTED",
    "CONFIRMED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
)

# Valid forward transitions. Anything not listed here is rejected by
# services/matching_service.py / routes/job_routes.py.
VALID_TRANSITIONS = {
    "POSTED": {"MATCHING", "CANCELLED"},
    "MATCHING": {"APPLICANTS", "CANCELLED"},
    "APPLICANTS": {"WORKER_SELECTED", "CANCELLED"},
    "WORKER_SELECTED": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"IN_PROGRESS", "CANCELLED"},
    "IN_PROGRESS": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractor_profiles.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    workers_required = db.Column(db.Integer, nullable=False, default=1)
    job_date = db.Column(db.Date, nullable=False)

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    area_text = db.Column(db.String(200), nullable=True)

    wage = db.Column(db.Float, nullable=False)
    working_hours = db.Column(db.String(50), nullable=True)
    min_experience = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default="POSTED", nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    skill = db.relationship("Skill")
    applications = db.relationship(
        "JobApplication", backref="job", cascade="all, delete-orphan", lazy="dynamic"
    )

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(self.status, set())

    def to_dict(self):
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "skill": self.skill.name if self.skill else None,
            "workers_required": self.workers_required,
            "job_date": self.job_date.isoformat() if self.job_date else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "area_text": self.area_text,
            "wage": self.wage,
            "working_hours": self.working_hours,
            "min_experience": self.min_experience,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
