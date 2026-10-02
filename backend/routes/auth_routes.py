"""
Authentication endpoints.

POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from services.auth_service import register_user, authenticate_user
from utils.validators import ValidationError
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Request body:
    {
      "email": "worker@skillpulse.local",
      "password": "Passw0rd123",
      "role": "worker" | "contractor",
      ... role-specific fields (see services/auth_service.py) ...
    }
    Response: 201 { "user": {...} }
    Errors: 400 { "error": "message" }
    """
    data = request.get_json(silent=True) or {}
    try:
        user = register_user(data)
        return jsonify({"user": user.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Registration failed. Please try again."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Request body: { "email": "...", "password": "..." }
    Response: 200 { "access_token": "...", "user": {...} }
    Errors: 401 { "error": "Invalid email or password." }
    """
    data = request.get_json(silent=True) or {}
    try:
        user = authenticate_user(data.get("email", ""), data.get("password", ""))
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "email": user.email},
        )
        return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Returns the currently authenticated user's basic info."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200
