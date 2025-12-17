"""
Script to create all database tables using SQLAlchemy models.
"""
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine
from models import (
    User, AnalysisHistory, Challenge, ChallengeParticipation,
    Friendship, Message, Achievement, UserAchievement, Goal,
    Post, PostLike, PostComment, DietPlan, WorkoutPlan,
    CompletedExercise, CompletedMeal,
    Exercise, BodyPart
)

def create_tables():
    """Create all tables defined in models."""
    print("Creating all database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
