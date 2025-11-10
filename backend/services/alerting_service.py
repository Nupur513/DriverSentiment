import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.driver import Driver
from models.alert import AlertLog
from backend.config import Config

class AlertingService:
    """
    Handles the logic for checking and raising alerts,
    including throttling.
    """
    
    def check_and_raise_alert(self, db: Session, driver_id: str, new_score: float):
        """
        Checks if the new score triggers an alert and if the alert
        is throttled.
        
        If an alert is raised, it's logged to the AlertLog table.
        """
        threshold = Config.ALERT_THRESHOLD
        
        if new_score >= threshold:
            # Score is good, no alert needed.
            return

        # Score is below threshold, check for throttling
        throttle_minutes = Config.ALERT_THROTTLE_MINUTES
        throttle_cutoff = datetime.now(timezone.utc) - timedelta(minutes=throttle_minutes)
        
        recent_alert = db.query(AlertLog).filter(
            AlertLog.driver_id == driver_id,
            AlertLog.timestamp >= throttle_cutoff
        ).first()
        
        if recent_alert:
            # An alert was already sent recently. Do nothing.
            logging.warning(f"Alert for driver {driver_id} is throttled. New score: {new_score}")
            return
            
        # --- Raise the Alert! ---
        # In a real system, this would trigger an email, SMS, or webhook.
        # For this demo, we'll log it to the console and the DB.
        
        print(f"!!! ALERT: Driver {driver_id} score dropped to {new_score:.2f} (Threshold: {threshold}) !!!")
        
        # Log the alert to the database
        new_alert_log = AlertLog(
            driver_id=driver_id,
            score_at_alert=new_score,
            threshold_at_alert=threshold
        )
        db.add(new_alert_log)
        
        # Commit is handled by the FeedbackProcessor