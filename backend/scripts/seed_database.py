"""
Example script to seed the database with sample data for a fitness tracking app.
"""
# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import bcrypt

from database import SessionLocal, engine, Base
from models import (
    User,
    Challenge,
    ChallengeParticipation,
    Friendship,
    AnalysisHistory,
    ExerciseType
)


def hash_password(password: str) -> str:

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_database():

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database with sample data...")

        # Create sample users
        users = [
            User(
                email="test",
                username="test",
                hashed_password=hash_password("test"),
                is_verified=True,
                points=2680,
                level=18,
                workouts_this_week=5,
                workouts_this_month=20,
                current_streak=7,
                status="On a 7-day streak",
                is_online=True
            ),
            User(
                email="test2",
                username="test2",
                hashed_password=hash_password("test2"),
                is_verified=True,
                points=2850,
                level=22,
                workouts_this_week=6,
                workouts_this_month=22,
                current_streak=10,
                status="Working out",
                is_online=True
            ),
            User(
                email="test3",
                username="test3",
                hashed_password=hash_password("test3"),
                is_verified=True,
                points=11240,
                level=35,
                workouts_this_week=7,
                workouts_this_month=24,
                current_streak=15,
                status="Rest day",
                is_online=True
            ),
            User(
                email="test4",
                username="test4",
                hashed_password=hash_password("test4"),
                is_verified=True,
                points=10650,
                level=28,
                workouts_this_week=6,
                workouts_this_month=23,
                current_streak=5,
                status="Completed leg day",
                is_online=False
            ),
            User(
                email="test5",
                username="test5",
                hashed_password=hash_password("test5"),
                is_verified=True,
                points=2420,
                level=15,
                workouts_this_week=5,
                workouts_this_month=18,
                current_streak=5,
                status="On a 5-day streak",
                is_online=True
            ),
            User(
                email="test6",
                username="test6",
                hashed_password=hash_password("test6"),
                is_verified=True,
                points=9880,
                level=28,
                workouts_this_week=6,
                workouts_this_month=21,
                current_streak=12,
                status="Morning workout completed",
                is_online=True
            ),
            User(
                email="test7",
                username="test7",
                hashed_password=hash_password("test7"),
                is_verified=True,
                points=2290,
                level=31,
                workouts_this_week=4,
                workouts_this_month=17,
                current_streak=3,
                status="Powerlifter | 500lb deadlift",
                is_online=False
            ),
            User(
                email="test8",
                username="test8",
                hashed_password=hash_password("test8"),
                is_verified=True,
                points=2180,
                level=24,
                workouts_this_week=5,
                workouts_this_month=19,
                current_streak=8,
                status="Marathon runner & yoga enthusiast",
                is_online=False
            ),
        ]

        for user in users:
            db.add(user)

        db.commit()
        print(f"✓ Created {len(users)} users")

        # Create friendships (Alex Johnson is the main user)
        alex = users[0]
        friendships = [
            Friendship(user_id=alex.id, friend_id=users[1].id, status="accepted"),  # Sarah
            Friendship(user_id=alex.id, friend_id=users[2].id, status="accepted"),  # Mike
            Friendship(user_id=alex.id, friend_id=users[3].id, status="accepted"),  # Emma
            Friendship(user_id=alex.id, friend_id=users[4].id, status="accepted"),  # James
        ]

        for friendship in friendships:
            db.add(friendship)

        db.commit()
        print(f"✓ Created {len(friendships)} friendships")

        # Create challenges
        now = datetime.now(timezone.utc)
        challenges = [
            Challenge(
                name="100 Mile March",
                description="Run or walk 100 miles this month",
                icon="Flame",
                target=100,
                unit="miles",
                reward_points=500,
                start_date=now - timedelta(days=18),
                end_date=now + timedelta(days=12)
            ),
            Challenge(
                name="Strength Week",
                description="Complete 5 strength workouts this week",
                icon="Dumbbell",
                target=5,
                unit="workouts",
                reward_points=250,
                start_date=now - timedelta(days=4),
                end_date=now + timedelta(days=3)
            ),
            Challenge(
                name="Early Bird Challenge",
                description="Complete morning workouts for 7 days straight",
                icon="Target",
                target=7,
                unit="days",
                reward_points=300,
                start_date=now + timedelta(days=1),
                end_date=now + timedelta(days=8)
            ),
        ]

        for challenge in challenges:
            db.add(challenge)

        db.commit()
        print(f"✓ Created {len(challenges)} challenges")

        participations = [
            ChallengeParticipation(
                user_id=alex.id,
                challenge_id=challenges[0].id,
                progress=68,
                completed=False
            ),
            ChallengeParticipation(
                user_id=alex.id,
                challenge_id=challenges[1].id,
                progress=3,
                completed=False
            ),
            # Add other users to challenges
            ChallengeParticipation(
                user_id=users[1].id,  
                challenge_id=challenges[0].id,
                progress=75,
                completed=False
            ),
            ChallengeParticipation(
                user_id=users[2].id, 
                challenge_id=challenges[0].id,
                progress=82,
                completed=False
            ),
            ChallengeParticipation(
                user_id=users[2].id,  
                challenge_id=challenges[1].id,
                progress=4,
                completed=False
            ),
        ]

        for participation in participations:
            db.add(participation)

        db.commit()
        print(f"✓ Created {len(participations)} challenge participations")


        analyses = [
            AnalysisHistory(
                user_id=alex.id,
                exercise_name=ExerciseType.biceps,
                video_filename="biceps_curl_1.mp4",
                feedback="Great form! Keep your elbows stable and control the descent.",
                avg_rating=92.5,
                joint_ratings={"elbow": 95, "shoulder": 90},
                processing_time=2.3
            ),
            AnalysisHistory(
                user_id=alex.id,
                exercise_name=ExerciseType.squats,
                video_filename="squats_1.mp4",
                feedback="Good depth! Try to keep your knees aligned with your toes.",
                avg_rating=88.0,
                joint_ratings={"knee": 85, "hip": 91},
                processing_time=3.1
            ),
            AnalysisHistory(
                user_id=alex.id,
                exercise_name=ExerciseType.pushups,
                video_filename="pushups_1.mp4",
                feedback="Excellent! Maintain that straight line from head to heels.",
                avg_rating=94.0,
                joint_ratings={"elbow": 95, "shoulder": 93},
                processing_time=2.8
            ),
        ]

        for analysis in analyses:
            db.add(analysis)

        db.commit()
        print(f"✓ Created {len(analyses)} analysis records")


    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
