import logging
import time
import threading # <-- 1. Add this import
from sqlalchemy.orm import Session
from models.feedback import Feedback, FeedbackEntityType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeedbackProcessor:
    """
    The main worker class. It pulls from the queue and uses
    the various services to process and store feedback.
    """
    def __init__(self, db_session_factory, queue_service, sentiment_service, scoring_service, alerting_service):
        self.db_session_factory = db_session_factory
        self.queue_service = queue_service
        self.sentiment_service = sentiment_service
        self.scoring_service = scoring_service
        self.alerting_service = alerting_service
        self.is_running = True
        self.worker_thread = None # <-- 2. Add a property to hold the thread

    def start_worker_thread(self): # <-- 3. Add this new method
        """
        Starts the worker loop in a new daemon thread.
        """
        self.worker_thread = threading.Thread(target=self.run_worker, daemon=True)
        self.worker_thread.start()

    def stop_worker(self): # <-- 4. Add this new method
        """
        Signals the worker thread to stop.
        """
        self.is_running = False
        # Optional: You could add a self.worker_thread.join(timeout=...) here
        # if you need to wait for it to finish gracefully.

    def run_worker(self):
        """
        The main loop for the worker thread.
        Continuously pulls tasks from the queue and processes them.
        """
        logging.info("Feedback worker is running...")
        while self.is_running:
            try:
                # This blocks until an item is available
                feedback_data = self.queue_service.get()
                
                # Process the message
                self.process_message(feedback_data)
                
                # Signal to the queue that task is done
                self.queue_service.task_done()
                
            except Exception as e:
                # Handle potential-poison-pill messages or DB errors
                logging.error(f"Error processing message: {feedback_data}. Error: {e}", exc_info=True)
                # In prod, we'd move this to a dead-letter queue
                
    def process_message(self, feedback_data: dict):
        """
        Processes a single feedback message.
        This includes sentiment analysis, saving, scoring, and alerting
        within a single database transaction.
        """
        logging.info(f"Processing feedback for: {feedback_data.get('entity_type')}:{feedback_data.get('entity_id')}")
        
        db: Session = self.db_session_factory()
        
        try:
            raw_text = feedback_data.get('text', '')
            entity_type_str = feedback_data.get('entity_type')
            entity_id = feedback_data.get('entity_id')
            user_id = feedback_data.get('user_id')

            # 1. Get Sentiment Score
            sentiment_score = self.sentiment_service.classify(raw_text)
            
            # 2. Save the raw feedback log
            feedback_log = Feedback(
                user_id=user_id,
                entity_type=FeedbackEntityType(entity_type_str),
                entity_id=entity_id,
                text=raw_text,
                sentiment_score=sentiment_score
            )
            
            # If it's driver feedback, link it to the driver model
            if entity_type_str == FeedbackEntityType.DRIVER.value:
                feedback_log.driver_id = entity_id

            db.add(feedback_log)

            # 3. Update driver score and check alerts (if it's driver feedback)
            if entity_type_str == FeedbackEntityType.DRIVER.value:
                
                # This performs the atomic read-lock-update
                new_avg_score = self.scoring_service.update_driver_score(
                    db=db,
                    driver_id=entity_id,
                    new_feedback_score=sentiment_score
                )
                
                # This checks score and throttling
                self.alerting_service.check_and_raise_alert(
                    db=db,
                    driver_id=entity_id,
                    new_score=new_avg_score
                )
            
            # 4. Commit the transaction
            # All or nothing: save feedback, update score, log alert
            db.commit()
            logging.info(f"Successfully processed feedback for {entity_id}")

        except Exception as e:
            # If *any* part fails, roll back everything
            logging.error(f"Transaction failed for feedback: {feedback_data}. Rolling back. Error: {e}", exc_info=True)
            db.rollback()
            
        finally:
            # Always close the session
            db.close()