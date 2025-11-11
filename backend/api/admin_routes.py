from flask import Blueprint, jsonify, g, request
from models.driver import Driver, DriverScore
from models.feedback import Feedback
from config import Config
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request

admin_bp = Blueprint("admin_bp", __name__)

# -------------------------
#  Admin-only access decorator
# -------------------------
def admin_required():
    """
    Custom decorator that verifies a valid JWT and enforces admin-only access.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Verify JWT presence and validity
                verify_jwt_in_request()
                claims = get_jwt()

                # Require role=admin
                if claims.get("role") != "admin":
                    return jsonify({"error": "Access forbidden: Admin role required."}), 403

                # Proceed to protected route
                return fn(*args, **kwargs)

            except Exception as e:
                # Missing, expired, or invalid token
                return jsonify({"error": f"Authentication error: {str(e)}"}), 401

        return decorator
    return wrapper


# -------------------------
#  Admin Routes
# -------------------------

@admin_bp.route("/config", methods=["GET"])
@admin_required()
def get_config():
    """
    Fetch system configuration — accessible only to Admin users.
    """
    return jsonify({
        "alert_threshold": Config.ALERT_THRESHOLD,
        "feature_flags": Config.FEATURE_FLAGS,
        "ema_alpha": Config.EMA_ALPHA,
        "alert_throttle_minutes": Config.ALERT_THROTTLE_MINUTES
    })


@admin_bp.route("/config", methods=["POST"])
@admin_required()
def update_config():
    """
    Update system configuration — Admin only.
    """
    data = request.get_json()

    # Example: update only known keys
    if "alert_threshold" in data:
        Config.ALERT_THRESHOLD = data["alert_threshold"]
    if "ema_alpha" in data:
        Config.EMA_ALPHA = data["ema_alpha"]
    if "alert_throttle_minutes" in data:
        Config.ALERT_THROTTLE_MINUTES = data["alert_throttle_minutes"]

    # Feature flags can be replaced entirely or partially
    if "feature_flags" in data:
        Config.FEATURE_FLAGS.update(data["feature_flags"])

    return jsonify({
        "message": "Configuration updated successfully",
        "updated_config": {
            "alert_threshold": Config.ALERT_THRESHOLD,
            "feature_flags": Config.FEATURE_FLAGS,
            "ema_alpha": Config.EMA_ALPHA,
            "alert_throttle_minutes": Config.ALERT_THROTTLE_MINUTES
        }
    }), 200


@admin_bp.route("/driver/<string:driver_id>", methods=["GET"])
@admin_required()
def get_driver_analytics(driver_id):
    """
    Get analytics for a single driver — Admin only.
    """
    db = g.db

    # Fetch driver score
    driver_score = db.query(DriverScore).filter(DriverScore.driver_id == driver_id).first()

    if not driver_score:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

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

    # Get latest feedback
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
    }), 200
