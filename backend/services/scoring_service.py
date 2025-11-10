from sqlalchemy.orm import Session
from models.driver import Driver, DriverScore
from backend.config import Config

class ScoringService:
    """
    Handles the logic for updating a driver's score.
    Uses an Exponential Moving Average (EMA) for real-time updates.
    """
    
    def update_driver_score(self, db: Session, driver_id: str, new_feedback_score: float) -> float:
        """
        Updates a driver's score using an atomic DB transaction.
        
        This function MUST be called within an active DB session.
        It uses `with_for_update()` to place a row-level lock on the
        DriverScore entry, preventing race conditions. This is the
        critical part that replaces the need for a tool like Redis
        for atomic updates.
        
        Returns:
            The new average score for the driver.
        """
        
        # Atomically get and lock the driver's score row
        driver_score = db.query(DriverScore).filter(
            DriverScore.driver_id == driver_id
        ).with_for_update().first()
        
        if not driver_score:
            # First-time feedback for this driver
            
            # Ensure driver exists (or create a stub)
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                driver = Driver(id=driver_id, name=f"Driver {driver_id}")
                db.add(driver)
            
            driver_score = DriverScore(
                driver_id=driver_id,
                average_sentiment_score=new_feedback_score, # First score is the average
                feedback_count=1
            )
            db.add(driver_score)
            new_ema = new_feedback_score
            
        else:
            # This driver already has a score, update it using EMA
            
            old_ema = driver_score.average_sentiment_score
            alpha = Config.EMA_ALPHA
            
            # The EMA formula
            new_ema = (new_feedback_score * alpha) + (old_ema * (1 - alpha))
            
            driver_score.average_sentiment_score = new_ema
            driver_score.feedback_count += 1
        
        # The session commit is handled by the FeedbackProcessor
        # after all steps (scoring, alerting) are done.
        
        return new_ema