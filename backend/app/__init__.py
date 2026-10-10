from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("FRONTEND_ORIGIN", "*")
            }
        }
    )

    # Import models
    with app.app_context():
        import models  # noqa: F401

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.worker_routes import worker_bp
    from routes.contractor_routes import contractor_bp
    from routes.job_routes import job_bp
    from routes.matching_routes import matching_bp
    from routes.admin_routes import admin_bp
    from routes.notification_routes import notification_bp
    from routes.public_routes import public_bp
    from routes.worker_photo_routes import worker_photo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(contractor_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(worker_photo_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "The requested resource was not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "error": "Method not allowed on this endpoint."
        }), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({
            "error": "An unexpected error occurred. Please try again."
        }), 500

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "SkillPulse backend"
        }), 200

    # Public statistics
    @app.route("/api/stats", methods=["GET"])
    def public_stats():
        from models.worker_profile import WorkerProfile
        from models.contractor_profile import ContractorProfile
        from models.job import Job

        verified_workers = WorkerProfile.query.filter_by(
            verification_status="verified"
        ).count()

        active_contractors = ContractorProfile.query.count()

        completed_jobs = Job.query.filter_by(
            status="COMPLETED"
        ).count()

        workers_with_ratings = WorkerProfile.query.filter(
            WorkerProfile.average_rating > 0
        ).all()

        if workers_with_ratings:
            average_rating = sum(
                worker.average_rating
                for worker in workers_with_ratings
            ) / len(workers_with_ratings)
        else:
            average_rating = 0

        return jsonify({
            "verified_workers": verified_workers,
            "active_contractors": active_contractors,
            "completed_jobs": completed_jobs,
            "average_rating": round(average_rating, 1)
        }), 200

    return app