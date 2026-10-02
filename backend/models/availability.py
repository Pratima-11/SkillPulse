"""
availability table.

One row per (worker, date). SkillPulse focuses on next-day availability,
so workers set this explicitly rather than the system assuming availability.
"""

from datetime import datetime, timezone
from app.extensions import db


class Availability(db.Model):
    __tablename__ = "availability"
    __table_args__ = (
        db.UniqueConstraint("worker_id", "available_date", name="uq_worker_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("worker_profiles.id"), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "available_date": self.available_date.isoformat() if self.available_date else None,
            "is_available": self.is_available,
        }
