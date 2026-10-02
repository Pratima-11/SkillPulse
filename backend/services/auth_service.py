"""
Authentication service - the logic behind register/login, kept out of the
route file so routes stay thin and this logic is independently testable.
"""

from app.extensions import db
from models.user import User
from models.worker_profile import WorkerProfile
from models.contractor_profile import ContractorProfile
from utils.validators import ValidationError, validate_email, validate_password, validate_role


def register_user(data: dict) -> User:
    email = validate_email(data.get("email", ""))
    password = validate_password(data.get("password", ""))
    role = validate_role(data.get("role", ""))
    if role == "admin":
        raise ValidationError("Admin accounts must be provisioned by an administrator.")

    if User.query.filter_by(email=email).first():
        raise ValidationError("An account with this email already exists.")

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # get user.id before committing, for the profile FK

    if role == "worker":
        full_name = data.get("full_name")
        phone = data.get("phone")
        if not full_name or not phone:
            raise ValidationError("full_name and phone are required for worker registration.")
        profile = WorkerProfile(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            expected_wage=float(data.get("expected_wage", 0)),
            experience_years=float(data.get("experience_years", 0)),
        )
        db.session.add(profile)

    elif role == "contractor":
        company_name = data.get("company_name")
        contact_person = data.get("contact_person")
        phone = data.get("phone")
        if not company_name or not contact_person or not phone:
            raise ValidationError(
                "company_name, contact_person and phone are required for contractor registration."
            )
        profile = ContractorProfile(
            user_id=user.id,
            company_name=company_name,
            contact_person=contact_person,
            phone=phone,
        )
        db.session.add(profile)

    db.session.commit()
    return user


def authenticate_user(email: str, password: str) -> User:
    email = validate_email(email)
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ValidationError("Invalid email or password.")
    if not user.is_active:
        raise ValidationError("This account has been deactivated. Contact the admin.")
    return user
