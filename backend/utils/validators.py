"""
Backend-side validation.

Per project rules (Section 20): the frontend also validates for UX, but
every one of these checks is re-run here because the frontend can always
be bypassed (Postman, curl, a modified request, etc).
"""

import re
from datetime import date, datetime

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    """Raised with a user-friendly message; caught centrally in app/__init__.py."""
    pass


def validate_email(email: str) -> str:
    if not email or not EMAIL_REGEX.match(email):
        raise ValidationError("A valid email address is required.")
    return email.strip().lower()


def validate_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain both letters and numbers.")
    return password


def validate_role(role: str) -> str:
    if role not in ("worker", "contractor", "admin"):
        raise ValidationError("Role must be one of: worker, contractor, admin.")
    return role


def validate_positive_number(value, field_name="value"):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number.")
    if number < 0:
        raise ValidationError(f"{field_name} must be a positive number.")
    return number


def validate_latitude(value):
    lat = validate_positive_number(abs(float(value)), "latitude") if value is not None else None
    if value is not None and not (-90 <= float(value) <= 90):
        raise ValidationError("Latitude must be between -90 and 90.")
    return float(value) if value is not None else None


def validate_longitude(value):
    if value is not None and not (-180 <= float(value) <= 180):
        raise ValidationError("Longitude must be between -180 and 180.")
    return float(value) if value is not None else None


def validate_date_not_past(value: str, field_name="date") -> date:
    """Ensures job/availability dates are today or later (jobs are next-day focused)."""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.")
    if parsed < date.today():
        raise ValidationError(f"{field_name} cannot be in the past.")
    return parsed


def validate_rating_value(value):
    try:
        rating = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Rating must be an integer between 1 and 5.")
    if not (1 <= rating <= 5):
        raise ValidationError("Rating must be between 1 and 5.")
    return rating


def require_fields(data: dict, fields: list):
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")
