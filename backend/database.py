from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config

# Create the SQLAlchemy engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create a thread-safe database session
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))

# Create a base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """
    Initializes the database and creates tables.
    This function imports all models that use `Base` so that they are
    registered with the metadata before creating the tables.
    """
    print("Initializing database...")
    
    # Import all models here to ensure they are registered with Base.metadata
    from models.user import User
    from models.driver import DriverScore
    from models.feedback import Feedback
    from models.alert import AlertLog
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")