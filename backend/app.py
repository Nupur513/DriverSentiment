import atexit
import logging
from flask import Flask, jsonify
from flask import g  # <-- add this import at the top

from flask_jwt_extended import JWTManager

from backend.config import Config
from backend.database import init_db, db_session
from services.feedback_processor import FeedbackProcessor
from services.queue_service import InMemoryQueue
# --- Add these imports ---
from services.sentiment_service import SimpleSentimentService
from services.scoring_service import ScoringService
from services.alerting_service import AlertingService
# -------------------------

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- App Initialization ---
def create_app():
    """
    Application factory function.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Service Initialization ---
    log.info("Initializing services...")
    
    # 1. Initialize all services
    queue_service = InMemoryQueue()
    sentiment_service = SimpleSentimentService()
    scoring_service = ScoringService()
    alerting_service = AlertingService()
    # The db_session is a scoped_session, which acts as a factory
    db_session_factory = db_session 

    # 2. Initialize the background worker
    # This processor will listen to the queue_service
    # --- FIX: Pass all required dependencies ---
    processor = FeedbackProcessor(
        db_session_factory=db_session_factory,
        queue_service=queue_service,
        sentiment_service=sentiment_service,
        scoring_service=scoring_service,
        alerting_service=alerting_service
    )
    # ---------------------------------------------
    
    # Start the background worker thread
    # The 'daemon=True' ensures the thread exits when the main app does
    processor.start_worker_thread()
    log.info("Background feedback processing worker started.")

    # --- JWT Initialization ---
    # Setup Flask-JWT-Extended
    jwt = JWTManager(app)
    log.info("JWTManager initialized.")

    # --- Database Initialization ---
    with app.app_context():
        init_db()

    # --- Register Blueprints (API Routes) ---
    log.info("Registering API blueprints...")
    
    # Import and register blueprints
    # We import here to avoid circular dependencies
    from api.feedback_routes import feedback_bp
    from api.admin_routes import admin_bp
    from api.auth_routes import auth_bp
    
    # Pass the queue_service to the feedback blueprint
    # This is a form of dependency injection
    feedback_bp.queue_service = queue_service 
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    log.info("Blueprints registered.")

    # --- Health Check Endpoint ---
    @app.route('/health')
    def health_check():
        """A simple health check endpoint."""
        return jsonify({"status": "healthy"}), 200
    @app.before_request

    def before_request():
        """Attach the database session to Flask's g object before each request."""
        g.db = db_session
        
    # --- Teardown ---
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove the database session at the end of the request."""
        db_session.remove()

    @atexit.register
    def shutdown_worker():
        """Stop the worker thread on application exit."""
        log.info("Shutting down feedback worker...")
        processor.stop_worker()

    return app

# --- Run Application ---
if __name__ == '__main__':
    app = create_app()
    # Note: Setting debug=False is important for production.
    # The reloader (debug=True) can cause issues with background threads.
    app.run(host='127.0.0.1', port=5000, debug=False)