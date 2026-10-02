"""
Entry point for the SkillPulse Flask backend.

Windows PowerShell / CMD usage (from the backend/ folder, with the venv active):
    python run.py

This will:
  1. Create the Flask app via the application factory.
  2. Create any missing database tables (safe to run repeatedly - it does
     NOT drop or overwrite existing tables).
  3. Start the development server on http://localhost:5000
"""

from app import create_app
from app.extensions import db

app = create_app()
if not app.config.get("SQLALCHEMY_DATABASE_URI"):
    raise RuntimeError("DATABASE_URL is not configured. Copy backend/.env.example to backend/.env and set your MySQL connection string.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables verified/created.")

    app.run(host="0.0.0.0", port=5000, debug=True)
