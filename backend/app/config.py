"""
Application configuration.

Reads all sensitive/environment-specific values from the .env file so that
no secret or password is ever hard-coded in source control.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env from the backend/ root (one level up from this file's folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///skillpulse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # avoids "MySQL server has gone away" errors
    }

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    )

    DEFAULT_MATCH_RADIUS_KM = float(os.environ.get("DEFAULT_MATCH_RADIUS_KM", 10))

    # Path to the matching weights configuration (Section 8 requirement:
    # weights must be configurable, not hard-coded in logic).
    MATCHING_WEIGHTS_PATH = os.path.join(BASE_DIR, "config", "matching_weights.json")

    # Path to the trained ML reliability model (created in Phase 4).
    ML_MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "reliability_model.pkl")
