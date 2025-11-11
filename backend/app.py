import atexit
import sys
import os
import logging
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# --- Add backend path to sys.path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Local imports ---
from config import Config
from database import init_db, db_session
from services.feedback_processor import FeedbackProcessor
from services.queue_service import InMemoryQueue
from services.sentiment_service import SimpleSentimentService
from services.scoring_service import ScoringService
from services.alerting_service import AlertingService

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- App Factory ---
def create_app():
    """
    Application factory function.
    """
    app = Flask(__name__)
    # Enable CORS for frontend on localhost:3000 (React dev server)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)

    # --- Initialize Services ---
    log.info("Initializing services...")
    queue_service = InMemoryQueue()
    sentiment_service = SimpleSentimentService()
    scoring_service = ScoringService()
    alerting_service = AlertingService()
    db_session_factory = db_session

    # --- Start Background Worker ---
    processor = FeedbackProcessor(
        db_session_factory=db_session_factory,
        queue_service=queue_service,
        sentiment_service=sentiment_service,
        scoring_service=scoring_service,
        alerting_service=alerting_service
    )
    processor.start_worker_thread()
    log.info("Background feedback processing worker started.")

    # --- JWT Setup ---
    jwt = JWTManager(app)
    log.info("JWTManager initialized.")

    # --- Database Initialization ---
    with app.app_context():
        init_db()

    # --- Register Blueprints ---
    log.info("Registering API blueprints...")

    # Import routes from backend/api
    from backend.api.feedback_routes import feedback_bp
    from backend.api.admin_routes import admin_bp
    from backend.api.auth_routes import auth_bp

    feedback_bp.queue_service = queue_service

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    log.info("Blueprints registered successfully.")

    # --- Health Check ---
    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"}), 200

    # --- Before/After Request Handlers ---
    @app.before_request
    def before_request():
        g.db = db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # --- Graceful Exit ---
    @atexit.register
    def shutdown_worker():
        log.info("Shutting down feedback worker...")
        processor.stop_worker()

    return app


# --- Run Server ---
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=False)
