"""
Role-based access control decorator.

Wraps flask_jwt_extended's identity check with a role check, so routes
can declare @role_required("worker") and get both authentication AND
authorization enforced in one line.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"This action requires role(s): {', '.join(allowed_roles)}."
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
