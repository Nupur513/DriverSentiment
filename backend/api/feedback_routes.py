import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config

log = logging.getLogger(__name__)

# Create a Blueprint
# The 'queue_service' will be injected from app.py
feedback_bp = Blueprint('feedback_api', __name__)

@feedback_bp.route('', methods=['POST'])
@jwt_required() # <-- Add this decorator to protect the route
def submit_feedback():
    """
    Accepts a new feedback submission from a logged-in user.
    Instead of processing it synchronously, it places the job
    onto the in-memory queue.
    """
    data = request.get_json()
    
    # --- Get user_id from the JWT token ---
    # This is more secure than trusting the request body
    try:
        current_user_id = get_jwt_identity()
    except Exception as e:
        log.warning(f"Error getting JWT identity: {e}")
        return jsonify({"error": "Invalid authentication token"}), 401
    
    # --- Extract data from request body ---
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    text = data.get('text')

    # Basic validation
    if not all([entity_type, entity_id, text]):
        log.warning("Feedback submission failed validation: Missing fields")
        return jsonify({"error": "Missing fields. 'entity_type', 'entity_id', and 'text' are required."}), 400

    # --- Feature Flag Check ---
    # Check if this feedback type is enabled in the config
    if entity_type not in Config.FEATURE_FLAGS or not Config.FEATURE_FLAGS[entity_type]:
        log.warning(f"Feedback submission rejected: Feature flag for '{entity_type}' is disabled.")
        return jsonify({"error": f"Feedback for entity type '{entity_type}' is currently disabled"}), 400

    # --- Construct the Job Payload ---
    # We now include the authenticated user_id
    feedback_job_data = {
        "user_id": current_user_id, # <-- Use the ID from the token
        "entity_type": entity_type,
        "entity_id": entity_id,
        "text": text
    }

    try:
        # Access the queue service injected during app creation
        queue = getattr(feedback_bp, 'queue_service', None)
        if not queue:
            log.error("Queue service is not initialized on feedback_bp.")
            return jsonify({"error": "Internal server error: Queue not available"}), 500
            
        # Put the job on the queue for the background worker
        queue.put(feedback_job_data)
        
        log.info(f"Queued feedback for {entity_type}:{entity_id} from user {current_user_id}")
        
        # Return 202 Accepted: The request has been accepted for processing,
        # but the processing is not yet complete.
        return jsonify({"message": "Feedback successfully queued for processing"}), 202

    except Exception as e:
        log.error(f"Failed to queue feedback: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error: {e}"}), 500