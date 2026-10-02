"""
users table.

Every account (worker, contractor, admin) has exactly one row here.
Passwords are NEVER stored in plain text - only a bcrypt hash.
"""

from datetime import datetime, timezone
import bcrypt
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("worker", "contractor", "admin", name="user_role"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # One-to-one relationships (only one of these will be populated,
    # depending on `role`).
    worker_profile = db.relationship(
        "WorkerProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    contractor_profile = db.relationship(
        "ContractorProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", backref="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_password(self, plain_password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
