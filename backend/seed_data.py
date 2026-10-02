"""
Seeds the database with demo accounts and sample data for demonstration.

WHY THIS IS A PYTHON SCRIPT AND NOT A .sql FILE:
Passwords must be bcrypt-hashed exactly the way models/user.py hashes them
at registration time. A hand-written hash pasted into a .sql file could
easily be wrong or inconsistent with the app's own hashing (salt rounds,
encoding, etc). Running this through the real User.set_password() method
guarantees the seeded demo accounts can actually log in.

Run from the backend/ folder, with the virtual environment active and
the database already created (see README):

    python seed_data.py

Safe to re-run: it checks for existing records before inserting so it
will not create duplicates.
"""

from datetime import date, timedelta

from app import create_app
from app.extensions import db
from models.user import User
from models.worker_profile import WorkerProfile
from models.contractor_profile import ContractorProfile
from models.skill import Skill
from models.availability import Availability
from models.job import Job

# Demo password - clearly a placeholder for local demonstration only,
# never a real credential.
DEMO_PASSWORD = "Demo@1234"

SKILL_NAMES = ["Painter", "Plumber", "Mason", "Electrician", "Carpenter"]

# Sample coordinates around Bangalore, spread a few km apart so the
# location scoring/radius filtering has something meaningful to do.
BANGALORE_LOCATIONS = {
    "Koramangala": (12.9352, 77.6245),
    "Indiranagar": (12.9719, 77.6412),
    "Whitefield": (12.9698, 77.7500),
    "Electronic City": (12.8452, 77.6602),
    "Jayanagar": (12.9308, 77.5838),
    "HSR Layout": (12.9121, 77.6446),
}


def get_or_create_skill(name):
    skill = Skill.query.filter_by(name=name).first()
    if not skill:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()
    return skill


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ---------------- Skills ----------------
        skills = {name: get_or_create_skill(name) for name in SKILL_NAMES}
        db.session.commit()
        print(f"Skills ready: {list(skills.keys())}")

        # ---------------- Admin ----------------
        if not User.query.filter_by(email="admin@skillpulse.local").first():
            admin = User(email="admin@skillpulse.local", role="admin")
            admin.set_password(DEMO_PASSWORD)
            db.session.add(admin)
            print("Created demo admin: admin@skillpulse.local")
        db.session.commit()

        # ---------------- Demo contractor ----------------
        contractor_user = User.query.filter_by(email="contractor@skillpulse.local").first()
        if not contractor_user:
            contractor_user = User(email="contractor@skillpulse.local", role="contractor")
            contractor_user.set_password(DEMO_PASSWORD)
            db.session.add(contractor_user)
            db.session.flush()

            lat, lng = BANGALORE_LOCATIONS["Koramangala"]
            contractor_profile = ContractorProfile(
                user_id=contractor_user.id,
                company_name="Bangalore Build Co.",
                contact_person="Ramesh Gowda",
                phone="9900011122",
                latitude=lat,
                longitude=lng,
                area_text="Koramangala, Bangalore",
            )
            db.session.add(contractor_profile)
            print("Created demo contractor: contractor@skillpulse.local")
        db.session.commit()

        contractor_profile = ContractorProfile.query.filter_by(user_id=contractor_user.id).first()

        # ---------------- Demo workers (matches Section 28 test case) ----------------
        # Worker A: Painter, available tomorrow, 3km-ish away, wage 750, decent history
        # Worker B: Painter, NOT available tomorrow, close by
        # Worker C: Plumber (wrong skill), available, farther away
        tomorrow = date.today() + timedelta(days=1)

        demo_workers = [
            {
                "email": "worker@skillpulse.local",
                "full_name": "Suresh Kumar (Worker A)",
                "phone": "9988877766",
                "skill": "Painter",
                "location": "HSR Layout",  # ~3km from Koramangala
                "expected_wage": 750,
                "experience_years": 4,
                "jobs_completed": 8,
                "jobs_accepted": 9,
                "jobs_cancelled": 1,
                "average_rating": 4.5,
                "verification_status": "verified",
                "available_tomorrow": True,
            },
            {
                "email": "worker_b@skillpulse.local",
                "full_name": "Manoj Reddy (Worker B)",
                "phone": "9988877767",
                "skill": "Painter",
                "location": "Indiranagar",  # ~2km-ish from Koramangala
                "expected_wage": 780,
                "experience_years": 2,
                "jobs_completed": 3,
                "jobs_accepted": 5,
                "jobs_cancelled": 2,
                "average_rating": 3.8,
                "verification_status": "verified",
                "available_tomorrow": False,  # deliberately unavailable
            },
            {
                "email": "worker_c@skillpulse.local",
                "full_name": "Farid Ahmed (Worker C)",
                "phone": "9988877768",
                "skill": "Plumber",  # wrong skill for the demo painting job
                "location": "Whitefield",
                "expected_wage": 700,
                "experience_years": 5,
                "jobs_completed": 10,
                "jobs_accepted": 10,
                "jobs_cancelled": 0,
                "average_rating": 4.8,
                "verification_status": "verified",
                "available_tomorrow": True,
            },
        ]

        created_worker_profiles = []
        for w in demo_workers:
            user = User.query.filter_by(email=w["email"]).first()
            if not user:
                user = User(email=w["email"], role="worker")
                user.set_password(DEMO_PASSWORD)
                db.session.add(user)
                db.session.flush()

                lat, lng = BANGALORE_LOCATIONS[w["location"]]
                profile = WorkerProfile(
                    user_id=user.id,
                    full_name=w["full_name"],
                    phone=w["phone"],
                    latitude=lat,
                    longitude=lng,
                    area_text=f"{w['location']}, Bangalore",
                    expected_wage=w["expected_wage"],
                    experience_years=w["experience_years"],
                    verification_status=w["verification_status"],
                    jobs_completed=w["jobs_completed"],
                    jobs_accepted=w["jobs_accepted"],
                    jobs_cancelled=w["jobs_cancelled"],
                    average_rating=w["average_rating"],
                )
                profile.skills = [skills[w["skill"]]]
                db.session.add(profile)
                db.session.flush()

                availability = Availability(
                    worker_id=profile.id,
                    available_date=tomorrow,
                    is_available=w["available_tomorrow"],
                )
                db.session.add(availability)

                # Set reliability using the same rule-based formula the app uses
                from services.reliability_service import update_worker_reliability
                update_worker_reliability(profile)

                created_worker_profiles.append(profile)
                print(f"Created demo worker: {w['email']}")

        db.session.commit()

        # ---------------- Demo job (the Section 28 test case job) ----------------
        existing_demo_job = Job.query.filter_by(
            contractor_id=contractor_profile.id, description="Interior wall painting - SkillPulse demo job"
        ).first()
        if not existing_demo_job:
            job = Job(
                contractor_id=contractor_profile.id,
                skill_id=skills["Painter"].id,
                workers_required=1,
                job_date=tomorrow,
                latitude=contractor_profile.latitude,
                longitude=contractor_profile.longitude,
                area_text=contractor_profile.area_text,
                wage=800,
                working_hours="9:00 AM - 5:00 PM",
                min_experience=1,
                description="Interior wall painting - SkillPulse demo job",
                status="POSTED",
            )
            db.session.add(job)
            db.session.commit()
            print(f"Created demo job #{job.id}: Painter needed tomorrow, wage 800, radius 10km")

        print("\nSeeding complete.")
        print("Demo login credentials (password for all: Demo@1234):")
        print("  Admin:      admin@skillpulse.local")
        print("  Contractor: contractor@skillpulse.local")
        print("  Worker A (should rank highest): worker@skillpulse.local")
        print("  Worker B (unavailable tomorrow, should be excluded): worker_b@skillpulse.local")
        print("  Worker C (wrong skill, should be excluded): worker_c@skillpulse.local")


if __name__ == "__main__":
    seed()
