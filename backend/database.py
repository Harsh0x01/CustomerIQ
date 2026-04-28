from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Engine = the actual connection to the database
# In production, we'd add pooling: pool_size=5, max_overflow=10
engine = create_engine(settings.DATABASE_URL)

# SessionLocal = a factory that creates database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = all your database table classes will inherit from this
Base = declarative_base()

def get_db():
    """
    FastAPI dependency to provide a database session.
    Automatically handles session closure after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
