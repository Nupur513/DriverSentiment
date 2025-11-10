from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class AlertLog(Base):
    """
    Model to log every time an alert is successfully triggered.
    This is used for the admin dashboard and for throttling.
    """
    __tablename__ = 'alert_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(String, ForeignKey('drivers.id'), nullable=False, index=True)
    
    # The score that triggered this alert
    score_at_alert = Column(Float, nullable=False)
    
    # The threshold that was active at the time
    threshold_at_alert = Column(Float, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    driver = relationship("Driver", back_populates="alerts")