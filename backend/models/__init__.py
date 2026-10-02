"""
Importing every model here ensures that when app/__init__.py calls
db.create_all(), SQLAlchemy's metadata already knows about every table -
otherwise tables that are never imported would silently not get created.
"""

from models.user import User
from models.skill import Skill, worker_skills
from models.worker_profile import WorkerProfile
from models.contractor_profile import ContractorProfile
from models.job import Job
from models.job_application import JobApplication
from models.availability import Availability
from models.rating import Rating
from models.notification import Notification

__all__ = [
    "User",
    "Skill",
    "worker_skills",
    "WorkerProfile",
    "ContractorProfile",
    "Job",
    "JobApplication",
    "Availability",
    "Rating",
    "Notification",
]
