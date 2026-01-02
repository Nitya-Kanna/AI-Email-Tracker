# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Determine if we're using PostgreSQL or SQLite
is_postgres = settings.DATABASE_URL.startswith("postgresql://") or settings.DATABASE_URL.startswith("postgres://")

# Create database engine
# This is the "connection" to your database
if is_postgres:
    # PostgreSQL (Railway production)
    engine = create_engine(settings.DATABASE_URL)
else:
    # SQLite (local development)
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

# Session factory - creates database sessions
# A session is like a "conversation" with the database
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-save changes
    autoflush=False,   # Don't auto-flush changes
    bind=engine        # Use the engine we created above
)

# Base class for all models (database tables)
# All your models will inherit from this
Base = declarative_base()

# Dependency function - provides database session to endpoints
def get_db():
    """
    Creates a database session for each request
    Automatically closes it when request is done
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the endpoint
    finally:
        db.close()  # Always close when done