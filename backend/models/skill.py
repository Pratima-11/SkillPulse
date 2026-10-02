"""
skills table + worker_skills (many-to-many join table).
"""

from app.extensions import db

# Many-to-many association table: a worker can have several skills,
# and a skill can belong to several workers.
worker_skills = db.Table(
    "worker_skills",
    db.Column("worker_id", db.Integer, db.ForeignKey("worker_profiles.id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id"), primary_key=True),
)


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}
