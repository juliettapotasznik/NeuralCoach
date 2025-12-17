"""
Example script to seed the database with sample challenges for a fitness tracking app.
"""
from database import SessionLocal
from models import Challenge
from datetime import datetime, timezone, timedelta


def seed_challenges():

    db = SessionLocal()

    try:
        # Check if challenges already exist
        existing = db.query(Challenge).count()
        if existing > 0:
            print(f"Challenges already exist ({existing} found). Skipping seed.")
            return

        now = datetime.now(timezone.utc)

        challenges = [
            Challenge(
                name="7-Day Streak Challenge",
                description="Train for 7 consecutive days",
                icon="Flame",
                target=7,
                unit="days",
                reward_points=100,
                start_date=now,
                end_date=now + timedelta(days=30)
            ),
            Challenge(
                name="50 Workouts Challenge",
                description="Complete 50 workouts this month",
                icon="Dumbbell",
                target=50,
                unit="workouts",
                reward_points=250,
                start_date=now,
                end_date=now + timedelta(days=30)
            ),
            Challenge(
                name="Perfect Form Challenge",
                description="Get 10 workouts with 90+ rating",
                icon="Target",
                target=10,
                unit="workouts",
                reward_points=150,
                start_date=now,
                end_date=now + timedelta(days=30)
            ),
        ]

        for challenge in challenges:
            db.add(challenge)

        db.commit()
        print(f"Successfully seeded {len(challenges)} challenges!")

    except Exception as e:
        print(f"Error seeding challenges: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_challenges()
