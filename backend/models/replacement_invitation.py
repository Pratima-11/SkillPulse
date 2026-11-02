"""
Replacement invitations for filling vacant worker positions.

Invitations are stored separately from job applications so the existing
application lifecycle and its unique (job_id, worker_id) constraint remain
unchanged.
"""

from datetime import datetime, timezone
from app.extensions import db


class ReplacementInvitation(db.Model):
    __tablename__ = "replacement_invitations"

    __table_args__ = (
        db.Index(
            "ix_replacement_invitation_job_status",
            "job_id",
            "status",
        ),
        db.Index(
            "ix_replacement_invitation_worker_status",
            "worker_id",
            "status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False,
    )
    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("worker_profiles.id"),
        nullable=False,
    )
    contractor_id = db.Column(
        db.Integer,
        db.ForeignKey("contractor_profiles.id"),
        nullable=False,
    )

    status = db.Column(
        db.Enum(
            "PENDING",
            "ACCEPTED",
            "REJECTED",
            "EXPIRED",
            "CANCELLED",
            name="replacement_invitation_status",
        ),
        nullable=False,
        default="PENDING",
    )

    match_score = db.Column(db.Float, nullable=True)
    score_breakdown = db.Column(db.JSON, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    responded_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "contractor_id": self.contractor_id,
            "status": self.status,
            "match_score": self.match_score,
            "score_breakdown": self.score_breakdown,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "responded_at": (
                self.responded_at.isoformat() if self.responded_at else None
            ),
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
        }


