"""
ratings table.

Created by a contractor after a job_application reaches COMPLETED.
Feeds back into worker_profiles.average_rating and reliability_score.
"""

from datetime import datetime, timezone
from app.extensions import db


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    job_application_id = db.Column(
        db.Integer, db.ForeignKey("job_applications.id"), unique=True, nullable=False
    )
    rating_value = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint("rating_value >= 1 AND rating_value <= 5", name="chk_rating_range"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_application_id": self.job_application_id,
            "rating_value": self.rating_value,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
