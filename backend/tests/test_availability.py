from datetime import date, timedelta

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from models import User, WorkerProfile, Skill, Availability


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "skillpulse-test-jwt-secret-key-minimum-32-bytes"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def availability_client(app):
    with app.app_context():
        user = User(
            email="availability-worker@test.local",
            password_hash="test-hash",
            role="worker",
        )
        db.session.add(user)
        db.session.flush()

        worker = WorkerProfile(
            user_id=user.id,
            full_name="Availability Test Worker",
            phone="9000000011",
            verification_status="verified",
        )
        db.session.add(worker)
        db.session.flush()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": "worker"},
        )
        worker_id = worker.id
        db.session.commit()

    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client, worker_id


def test_set_availability(availability_client, app):
    client, worker_id = availability_client
    target_date = date.today() + timedelta(days=5)

    response = client.post(
        "/api/worker/availability",
        json={"available_date": target_date.isoformat(), "is_available": True},
    )

    assert response.status_code == 200, response.get_json()
    assert response.json["availability"]["is_available"] is True

    with app.app_context():
        rows = Availability.query.filter_by(
            worker_id=worker_id, available_date=target_date
        ).all()
        assert len(rows) == 1
        assert rows[0].is_available is True


def test_update_availability_to_unavailable(availability_client, app):
    client, worker_id = availability_client
    target_date = date.today() + timedelta(days=5)

    first = client.post(
        "/api/worker/availability",
        json={"available_date": target_date.isoformat(), "is_available": True},
    )
    assert first.status_code == 200, first.get_json()

    response = client.post(
        "/api/worker/availability",
        json={"available_date": target_date.isoformat(), "is_available": False},
    )

    assert response.status_code == 200, response.get_json()
    assert response.json["availability"]["is_available"] is False

    with app.app_context():
        rows = Availability.query.filter_by(
            worker_id=worker_id, available_date=target_date
        ).all()
        assert len(rows) == 1
        assert rows[0].is_available is False


def test_reject_past_availability_date(availability_client):
    client, _ = availability_client
    target_date = date.today() - timedelta(days=1)

    response = client.post(
        "/api/worker/availability",
        json={"available_date": target_date.isoformat(), "is_available": True},
    )

    assert response.status_code == 400


def test_reject_invalid_availability_date(availability_client):
    client, _ = availability_client

    response = client.post(
        "/api/worker/availability",
        json={"available_date": "not-a-date", "is_available": True},
    )

    assert response.status_code == 400

def test_matching_respects_worker_availability(availability_client, app):
    from models import ContractorProfile, Skill, Job
    from app.config import Config
    from services.matching_service import rank_workers_for_job

    client, worker_id = availability_client
    target_date = date.today() + timedelta(days=5)

    # Set the worker as available for the job date.
    response = client.post(
        "/api/worker/availability",
        json={
            "available_date": target_date.isoformat(),
            "is_available": True,
        },
    )
    assert response.status_code == 200, response.get_json()

    with app.app_context():
        worker = WorkerProfile.query.get(worker_id)
        worker.latitude = 12.9716
        worker.longitude = 77.5946
        worker.expected_wage = 400
        worker.experience_years = 2

        skill = Skill(name="Availability Integration Test Skill")
        contractor_user = User(
            email="availability-contractor@test.local",
            password_hash="test-hash",
            role="contractor",
        )
        db.session.add_all([skill, contractor_user])
        db.session.flush()

        worker.skills.append(skill)

        contractor = ContractorProfile(
            user_id=contractor_user.id,
            company_name="Availability Test Company",
            contact_person="Test Contractor",
            phone="9000000012",
        )
        db.session.add(contractor)
        db.session.flush()

        job = Job(
            contractor_id=contractor.id,
            skill_id=skill.id,
            workers_required=1,
            job_date=target_date,
            latitude=12.9716,
            longitude=77.5946,
            wage=500,
            min_experience=0,
            status="POSTED",
        )
        db.session.add(job)
        db.session.commit()

        # Available workers should qualify for matching.
        matches = rank_workers_for_job(
            job, [worker], Config.MATCHING_WEIGHTS_PATH
        )
        assert any(item["worker"].id == worker_id for item in matches), (
            "Available worker was unexpectedly excluded from matching."
        )

    # Mark the same worker unavailable for the same date.
    response = client.post(
        "/api/worker/availability",
        json={
            "available_date": target_date.isoformat(),
            "is_available": False,
        },
    )
    assert response.status_code == 200, response.get_json()

    with app.app_context():
        worker = WorkerProfile.query.get(worker_id)
        job = Job.query.filter_by(
            job_date=target_date,
            contractor_id=ContractorProfile.query.filter_by(
                company_name="Availability Test Company"
            ).first().id,
        ).first()

        matches = rank_workers_for_job(
            job, [worker], Config.MATCHING_WEIGHTS_PATH
        )
        assert not any(
            item["worker"].id == worker_id for item in matches
        ), "Unavailable worker was incorrectly included in matching."

    # Restore availability and verify the worker qualifies again.
    response = client.post(
        "/api/worker/availability",
        json={
            "available_date": target_date.isoformat(),
            "is_available": True,
        },
    )
    assert response.status_code == 200, response.get_json()

    with app.app_context():
        worker = WorkerProfile.query.get(worker_id)
        job = Job.query.filter_by(
            job_date=target_date,
            contractor_id=ContractorProfile.query.filter_by(
                company_name="Availability Test Company"
            ).first().id,
        ).first()

        matches = rank_workers_for_job(
            job, [worker], Config.MATCHING_WEIGHTS_PATH
        )
        assert any(
            item["worker"].id == worker_id for item in matches
        ), "Worker was not eligible after availability was restored."
