from flask import Blueprint, jsonify, g
from models.driver import Driver, DriverScore
from models.feedback import Feedback
from backend.config import Config

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/config', methods=['GET'])
def get_config():
    """
    Endpoint for the Admin UI to fetch system configuration.
    """
    return jsonify({
        "alert_threshold": Config.ALERT_THRESHOLD,
        "feature_flags": Config.FEATURE_FLAGS,
        "ema_alpha": Config.EMA_ALPHA,
        "alert_throttle_minutes": Config.ALERT_THROTTLE_MINUTES
    })
    
# TODO: Add a POST /config endpoint with authentication to update these.

@admin_bp.route('/driver/<string:driver_id>', methods=['GET'])
def get_driver_analytics(driver_id):
    """
    Endpoint for the Admin Dashboard to get all data for a single driver.
    """
    db = g.db
    
    # Get the driver's current score
    driver_score = db.query(DriverScore).filter(DriverScore.driver_id == driver_id).first()
    
    if not driver_score:
        # Check if driver exists but just has no score yet
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return jsonify({"error": "Driver not found"}), 404
        # Driver exists but has no feedback
        score_data = {
            "driver_id": driver.id,
            "name": driver.name,
            "current_score": None,
            "feedback_count": 0
        }
    else:
        score_data = {
            "driver_id": driver_score.driver.id,
            "name": driver_score.driver.name,
            "current_score": round(driver_score.average_sentiment_score, 2),
            "feedback_count": driver_score.feedback_count
        }

    # Get recent feedback history (e.g., last 20)
    feedback_history = db.query(Feedback).filter(
        Feedback.driver_id == driver_id
    ).order_by(Feedback.created_at.desc()).limit(20).all()
    
    return jsonify({
        "analytics": score_data,
        "recent_feedback": [
            {
                "id": f.id,
                "text": f.text,
                "score": f.sentiment_score,
                "timestamp": f.created_at.isoformat()
            } for f in feedback_history
        ]
    })