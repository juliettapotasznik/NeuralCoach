"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load .env file but don't override existing environment variables (from Docker)
load_dotenv(override=False)

# Get database URL from environment variable

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to components if full URL not set
    user = os.getenv("POSTGRES_USER", "neuralcoach")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "neuralcoach_db")
    
    if password:
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        raise ValueError("POSTGRES_PASSWORD environment variable is required.")

# AWS RDS requires SSL connection
if "rds.amazonaws.com" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

# Configure engine arguments based on database type
engine_args = {
    "pool_pre_ping": True
}

# SQLite does not support pool_size/max_overflow with the default pool
if "sqlite" not in DATABASE_URL:
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    **engine_args
)


# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """

    from models import (
        User, AnalysisHistory, Challenge, ChallengeParticipation,
        Friendship, DietPlan, WorkoutPlan, Goal, Achievement,
        UserAchievement, Post, PostLike, PostComment, Message, BodyPart, Exercise, exercise_body_parts
    )
