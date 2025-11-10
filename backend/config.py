import os

# Get the absolute path of the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Central configuration for the application.
    """
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sentiment_engine.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT Configuration ---
    # !!IMPORTANT!!: Change this to a long, random, and secret string
    # You can generate one using: python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET_KEY = "CHANGE-THIS-IN-PRODUCTION-a-super-secret-key"

    # --- Business Logic Configuration ---
    
    # Alert threshold (e.g., 2.5 out of 5)
    ALERT_THRESHOLD = 2.5

    # Exponential Moving Average (EMA) smoothing factor.
    EMA_ALPHA = 0.1 

    # Alert throttling
    ALERT_THROTTLE_MINUTES = 60

    # --- Feature Flags ---
    FEATURE_FLAGS = {
        "DRIVER": True,
        "TRIP": True,
        "APP": True,
        "MARSHAL": False
    }