from sqlalchemy import Column, String, Integer, Text, DateTime, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from backend.database import Base
import enum

class FeedbackEntityType(enum.Enum):
    """Enum for the different types of feedback entities."""
    DRIVER = "DRIVER"
    TRIP = "TRIP"
    APP = "APP"
    MARSHAL = "MARSHAL"

class Feedback(Base):
    """
    Model for a single piece of feedback.
    This is the raw data.
    """
    __tablename__ = 'feedbacks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Configurable entity type
    entity_type = Column(Enum(FeedbackEntityType), nullable=False, index=True)
    
    # The ID of the entity being reviewed (e.g., driver_id, trip_id)
    entity_id = Column(String(100), nullable=False, index=True)
    
    # Raw text content
    text = Column(Text, nullable=True)
    
    # The score (1-5) assigned by the sentiment service
    sentiment_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- Example of relating to a driver ---
    # This setup allows us to link feedback to a driver *if*
    # the entity_type is DRIVER.
    driver_id = Column(String, ForeignKey('drivers.id'), nullable=True)
    driver = relationship("Driver", back_populates="feedbacks", foreign_keys=[driver_id])
    
    __mapper_args__ = {
        'polymorphic_on': entity_type,
    }

# We could create polymorphic subclasses, but for this design,
# simply checking `entity_type == 'DRIVER'` in the service is simpler.