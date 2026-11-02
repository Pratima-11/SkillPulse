from datetime import date, datetime, timedelta, timezone

import pytest
from flask_jwt_extended import create_access_token
from models import Availability
from app import create_app
from app.extensions import db
from models import (
    User, WorkerProfile, ContractorProfile, Skill, Job,
    JobApplication, ReplacementInvitation,
)


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
def setup_data(app):
    contractor_user = User(
        email="contractor@test.local",
        password_hash="test-hash",
        role="contractor",
    )
    worker_user = User(
        email="worker@test.local",
        password_hash="test-hash",
        role="worker",
    )
    other_user = User(
        email="other-worker@test.local",
        password_hash="test-hash",
        role="worker",
    )
    db.session.add_all([contractor_user, worker_user, other_user])
    db.session.flush()

    contractor = ContractorProfile(
        user_id=contractor_user.id,
        company_name="Test Construction",
        contact_person="Test Contractor",
        phone="9000000001",
    )
    worker = WorkerProfile(
        user_id=worker_user.id,
        full_name="Test Worker",
        phone="9000000002",
        verification_status="verified",
    )
    other_worker = WorkerProfile(
        user_id=other_user.id,
        full_name="Other Worker",
        phone="9000000003",
        verification_status="verified",
    )
    skill = Skill(name="Replacement Test Skill")
    db.session.add_all([contractor, worker, other_worker, skill])
    db.session.flush()

    worker.skills.append(skill)
    worker.expected_wage = 400
    worker.experience_years = 1
    worker.latitude = 12.9716
    worker.longitude = 77.5946

    db.session.add(Availability(
        worker_id=worker.id,
        available_date=date.today() + timedelta(days=1),
        is_available=True,
    ))

    job = Job(
        contractor_id=contractor.id,
        skill_id=skill.id,
        workers_required=2,
        job_date=date.today() + timedelta(days=1),
        latitude=12.9716,
        longitude=77.5946,
        wage=500,
        min_experience=0,
        status="CONFIRMED",
    )
    db.session.add(job)
    db.session.flush()

    db.session.add(JobApplication(
        job_id=job.id,
        worker_id=other_worker.id,
        status="SELECTED",
        match_score=0.8,
        score_breakdown={},
    ))

    invitation = ReplacementInvitation(
        job_id=job.id,
        worker_id=worker.id,
        contractor_id=contractor.id,
        status="PENDING",
        match_score=0.85,
        score_breakdown={},
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.session.add(invitation)
    db.session.commit()

    return {
        "contractor_user": contractor_user,
        "worker_user": worker_user,
        "worker": worker,
        "other_worker": other_worker,
        "contractor": contractor,
        "job": job,
        "invitation": invitation,
    }


def worker_headers(user):
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": "worker"},
    )
    return {"Authorization": f"Bearer {token}"}


def test_worker_can_accept_replacement_invitation(app, setup_data):
    data = setup_data
    client = app.test_client()

    response = client.post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/accept",
        headers=worker_headers(data["worker_user"]),
    )

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["invitation"]["status"] == "ACCEPTED"

    application = JobApplication.query.filter_by(
        job_id=data["job"].id,
        worker_id=data["worker"].id,
    ).first()

    assert application is not None
    assert application.status == "SELECTED"


def test_worker_can_reject_replacement_invitation(app, setup_data):
    data = setup_data
    client = app.test_client()

    response = client.post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/reject",
        headers=worker_headers(data["worker_user"]),
    )

    assert response.status_code == 200, response.get_json()
    db.session.refresh(data["invitation"])
    assert data["invitation"].status == "REJECTED"


def test_expired_invitation_cannot_be_accepted(app, setup_data):
    data = setup_data
    data["invitation"].expires_at = (
        datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db.session.commit()

    response = app.test_client().post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/accept",
        headers=worker_headers(data["worker_user"]),
    )

    assert response.status_code == 410, response.get_json()
    db.session.refresh(data["invitation"])
    assert data["invitation"].status == "EXPIRED"


def test_worker_cannot_accept_when_no_vacancies_remain(app, setup_data):
    data = setup_data
    data["job"].workers_required = 1
    db.session.commit()

    response = app.test_client().post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/accept",
        headers=worker_headers(data["worker_user"]),
    )

    assert response.status_code == 409, response.get_json()
    assert "vacancies" in response.get_json()["error"].lower()


def test_worker_cannot_accept_duplicate_application(app, setup_data):
    data = setup_data
    data["job"].workers_required = 3

    db.session.add(JobApplication(
        job_id=data["job"].id,
        worker_id=data["worker"].id,
        status="APPLIED",
        match_score=0.5,
        score_breakdown={},
    ))
    db.session.commit()

    response = app.test_client().post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/accept",
        headers=worker_headers(data["worker_user"]),
    )

    assert response.status_code == 409, response.get_json()
    assert "already have an application" in response.get_json()["error"].lower()


def test_worker_cannot_accept_another_workers_invitation(app, setup_data):
    data = setup_data
    client = app.test_client()

    response = client.post(
        f"/api/worker/replacement-invitations/{data['invitation'].id}/accept",
        headers=worker_headers(data["other_worker"].user),
    )

    assert response.status_code == 404, response.get_json()


def test_worker_invitations_require_authentication(app):
    response = app.test_client().get(
        "/api/worker/replacement-invitations"
    )

    assert response.status_code == 401, response.get_json()


def contractor_headers(user):
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": "contractor"},
    )
    return {"Authorization": f"Bearer {token}"}



def test_contractor_can_create_replacement_invitation(app, setup_data):
    data = setup_data

    # The shared fixture already creates an invitation for this worker.
    # Remove it so this test can verify creation of a new invitation.
    db.session.delete(data["invitation"])
    db.session.commit()

    client = app.test_client()
    response = client.post(
        f"/api/contractor/jobs/{data['job'].id}/replacement-invitations",
        headers=contractor_headers(data["contractor_user"]),
        json={"worker_id": data["worker"].id},
    )

    assert response.status_code == 201, response.get_json()
    assert response.get_json()["invitation"]["status"] == "PENDING"


def test_contractor_cannot_invite_worker_with_existing_application(app, setup_data):
    data = setup_data
    client = app.test_client()

    db.session.add(JobApplication(
        job_id=data["job"].id,
        worker_id=data["worker"].id,
        status="APPLIED",
        match_score=0.5,
        score_breakdown={},
    ))
    db.session.commit()

    response = client.post(
        f"/api/contractor/jobs/{data['job'].id}/replacement-invitations",
        headers=contractor_headers(data["contractor_user"]),
        json={"worker_id": data["worker"].id},
    )

    assert response.status_code == 409, response.get_json()

