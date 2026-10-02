"""
job_applications table.

This is the record created whenever a worker is matched against / applies
to a job. It carries the computed match_score so the score is never
recalculated silently later - it's stored at the moment of matching for
transparency and for the "why was I recommended" explanation in the UI.
"""

from datetime import datetime, timezone
from app.extensions import db

APPLICATION_STATUSES = ("PENDING", "SELECTED", "REJECTED", "CONFIRMED", "COMPLETED", "CANCELLED")


class JobApplication(db.Model):
    __tablename__ = "job_applications"
    __table_args__ = (
        db.UniqueConstraint("job_id", "worker_id", name="uq_job_worker"),
    )

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("worker_profiles.id"), nullable=False)

    match_score = db.Column(db.Float, nullable=False, default=0.0)
    score_breakdown = db.Column(db.JSON, nullable=True)  # stores per-factor scores for the UI

    status = db.Column(db.String(20), default="PENDING", nullable=False)

    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    rating = db.relationship(
        "Rating", backref="job_application", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "match_score": round(self.match_score, 2),
            "score_breakdown": self.score_breakdown,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
        }
