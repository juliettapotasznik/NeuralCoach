"""
SQLAlchemy database models for NeuralCoach.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, Boolean, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base
import enum


class ExerciseType(str, enum.Enum):
    """Supported exercise types"""
    biceps = "biceps"
    squats = "squats"
    pushups = "pushups"
    lunges = "lunges"
    plank = "plank"


class User(Base):
    """
    User model for authentication and profile management.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    profile_picture = Column(String(255), nullable=True)  # Path to profile picture
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship to analysis history
    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")

    # Community stats
    points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    workouts_this_week = Column(Integer, default=0, nullable=False)
    workouts_this_month = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    status = Column(String(255), nullable=True)  # User status message
    is_online = Column(Boolean, default=False, nullable=False)

    # Relationships to community features
    friendships_initiated = relationship("Friendship", foreign_keys="Friendship.user_id", back_populates="user", cascade="all, delete-orphan")
    friendships_received = relationship("Friendship", foreign_keys="Friendship.friend_id", back_populates="friend", cascade="all, delete-orphan")
    challenge_participations = relationship("ChallengeParticipation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class AnalysisHistory(Base):
    """
    Analysis history model to store user's exercise analysis results.
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_name = Column(String(255), nullable=False, index=True)
    video_filename = Column(String(255), nullable=True)
    feedback = Column(Text, nullable=True)
    avg_rating = Column(Float, nullable=True)
    joint_ratings = Column(JSON, nullable=True)  # Store per-joint scores as JSON
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship to user
    user = relationship("User", back_populates="analyses")

    def __repr__(self):
        return f"<AnalysisHistory(id={self.id}, user_id={self.user_id}, exercise={self.exercise_name})>"



class Challenge(Base):
    """
    Fitness challenge model.
    """
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=False)  # Icon name (e.g., "Flame", "Dumbbell")
    target = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)  # e.g., "miles", "workouts", "days"
    reward_points = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    participations = relationship("ChallengeParticipation", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Challenge(id={self.id}, name={self.name})>"


class ChallengeParticipation(Base):
    """
    User participation in challenges.
    """
    __tablename__ = "challenge_participations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="challenge_participations")
    challenge = relationship("Challenge", back_populates="participations")

    def __repr__(self):
        return f"<ChallengeParticipation(user_id={self.user_id}, challenge_id={self.challenge_id})>"


class Friendship(Base):
    """
    User friendships/connections.
    """
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, blocked
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="friendships_initiated")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friendships_received")

    def __repr__(self):
        return f"<Friendship(user_id={self.user_id}, friend_id={self.friend_id}, status={self.status})>"


class Message(Base):
    """
    Chat messages between users.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"


class Achievement(Base):
    """
    User achievements and badges.
    """
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "workout", "streak", "social"
    requirement = Column(Integer, nullable=False)  # Number required to unlock
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name})>"


class UserAchievement(Base):
    """
    User's unlocked achievements.
    """
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"


class Goal(Base):
    """
    User fitness goals.
    """
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0, nullable=False)
    unit = Column(String(50), nullable=False)  # e.g., "workouts", "calories", "days"
    deadline = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<Goal(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Post(Base):
    """
    Post model for community posts/updates.
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id})>"


class PostLike(Base):
    """
    PostLike model for tracking post likes.
    """
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<PostLike(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class PostComment(Base):
    """
    PostComment model for post comments.
    """
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class DietPlan(Base):
    """
    DietPlan model for storing user diet plans.
    """
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nutrition = Column(JSON, nullable=False)  # calories, protein, carbs, fat
    meal_plan = Column(JSON, nullable=False)  # list of meals
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<DietPlan(id={self.id}, user_id={self.user_id})>"


class WorkoutPlan(Base):
    """
    WorkoutPlan model for storing user workout plans.
    """
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(255), nullable=False)
    exercises = Column(JSON, nullable=False)  # list of exercises
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    completed_exercises = relationship("CompletedExercise", back_populates="workout_plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, user_id={self.user_id})>"


class CompletedExercise(Base):
    """
    CompletedExercise model for tracking completed exercises in a workout plan.
    """
    __tablename__ = "completed_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)
    exercise_index = Column(Integer, nullable=False)  # Index in the exercises JSON array
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    workout_plan = relationship("WorkoutPlan", back_populates="completed_exercises")

    def __repr__(self):
        return f"<CompletedExercise(id={self.id}, workout_plan_id={self.workout_plan_id}, exercise_index={self.exercise_index})>"


class CompletedMeal(Base):
    """
    CompletedMeal model for tracking completed meals in a diet plan.
    """
    __tablename__ = "completed_meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diet_plan_id = Column(Integer, ForeignKey("diet_plans.id"), nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    recipe_index = Column(Integer, nullable=False)  # Index in the recipes array for this meal type
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    diet_plan = relationship("DietPlan", foreign_keys=[diet_plan_id])

    def __repr__(self):
        return f"<CompletedMeal(id={self.id}, diet_plan_id={self.diet_plan_id}, meal_type={self.meal_type})>"

# Association table for many-to-many relationship between exercises and body parts
exercise_body_parts = Table(
    'exercise_body_parts',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercises.id', ondelete='CASCADE'), primary_key=True),
    Column('body_part_id', Integer, ForeignKey('body_parts.id', ondelete='CASCADE'), primary_key=True)
)


class BodyPart(Base):
    """
    Body parts lookup table.
    """
    __tablename__ = "body_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    exercises = relationship("Exercise", secondary=exercise_body_parts, back_populates="body_parts")

    def __repr__(self):
        return f"<BodyPart(id={self.id}, name={self.name})>"


class Exercise(Base):
    """
    Exercise model for exercise library.
    """
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    media_file = Column(String(255), nullable=False)  
    attribution = Column(Text, nullable=False)  
    description = Column(Text, nullable=False) 
    is_analyzable = Column(Boolean, default=False)

    body_parts = relationship("BodyPart", secondary=exercise_body_parts, back_populates="exercises")

    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name})>"

