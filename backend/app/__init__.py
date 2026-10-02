"""
Application factory.

create_app() wires together: config, extensions (db, jwt, cors), all
model imports (so db.create_all() knows about every table), all route
blueprints, and centralized error handlers so backend errors never leak
sensitive details to the frontend (Section 21).
"""

from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}})
    # NOTE: origins is "*" for local MCA-project demo convenience. For any
    # real deployment this should be restricted to the actual frontend origin.

    # --- Import models so SQLAlchemy metadata is complete before create_all ---
    with app.app_context():
        import models  # noqa: F401

    # --- Register blueprints ---
    from routes.auth_routes import auth_bp
    from routes.worker_routes import worker_bp
    from routes.contractor_routes import contractor_bp
    from routes.job_routes import job_bp
    from routes.matching_routes import matching_bp
    from routes.admin_routes import admin_bp
    from routes.notification_routes import notification_bp
    from routes.public_routes import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(contractor_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(public_bp)

    # --- Centralized error handlers (never leak internals to the client) ---
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "The requested resource was not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed on this endpoint."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "SkillPulse backend"}), 200

    return app
