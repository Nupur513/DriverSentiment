from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Driver(Base):
    """
    Model for a Driver.
    In a real system, this would be richer and likely sync'd from another service.
    """
    __tablename__ = 'drivers'
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    
    # Relationships
    score = relationship("DriverScore", back_populates="driver", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="driver")
    alerts = relationship("AlertLog", back_populates="driver")

class DriverScore(Base):
    """
    Model to hold the aggregated sentiment score for a driver.
    This table is the core of the real-time analytics.
    """
    __tablename__ = 'driver_scores'
    driver_id = Column(String, ForeignKey('drivers.id'), primary_key=True)
    
    # The current aggregated score (calculated via EMA)
    average_sentiment_score = Column(Float, nullable=False, default=3.0) 
    
    # Total number of feedback entries processed
    feedback_count = Column(Integer, nullable=False, default=0)
    
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    driver = relationship("Driver", back_populates="score")