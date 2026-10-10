"""Store worker photo metadata separately from worker profiles."""

from datetime import datetime, timezone

from app.extensions import db


class WorkerPhoto(db.Model):
    __tablename__ = "worker_photos"

    id = db.Column(db.Integer, primary_key=True)

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("worker_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    file_name = db.Column(db.String(255), nullable=False)

    uploaded_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )