"""
Example script to seed the database with sample achievements for a fitness tracking app.
"""
from database import SessionLocal
from models import Achievement
from datetime import datetime, timezone


def seed_achievements():

    db = SessionLocal()

    try:
        # Check if achievements already exist
        existing = db.query(Achievement).count()
        if existing > 0:
            print(f"Achievements already exist ({existing} found). Skipping seed.")
            return

        achievements = [
            # Workout achievements
            Achievement(
                name="First Steps",
                description="Complete your first workout",
                icon="Dumbbell",
                category="workout",
                requirement=1
            ),
            Achievement(
                name="Getting Started",
                description="Complete 10 workouts",
                icon="Dumbbell",
                category="workout",
                requirement=10
            ),
            Achievement(
                name="Dedicated Athlete",
                description="Complete 50 workouts",
                icon="Trophy",
                category="workout",
                requirement=50
            ),
            Achievement(
                name="Fitness Master",
                description="Complete 100 workouts",
                icon="Trophy",
                category="workout",
                requirement=100
            ),

            # Streak achievements
            Achievement(
                name="Consistency",
                description="Maintain a 7-day streak",
                icon="Flame",
                category="streak",
                requirement=7
            ),
            Achievement(
                name="On Fire",
                description="Maintain a 30-day streak",
                icon="Flame",
                category="streak",
                requirement=30
            ),
            Achievement(
                name="Unstoppable",
                description="Maintain a 100-day streak",
                icon="Flame",
                category="streak",
                requirement=100
            ),

            # Social achievements
            Achievement(
                name="Social Butterfly",
                description="Connect with 5 friends",
                icon="Users",
                category="social",
                requirement=5
            ),
            Achievement(
                name="Community Leader",
                description="Connect with 20 friends",
                icon="Users",
                category="social",
                requirement=20
            ),
        ]

        for achievement in achievements:
            db.add(achievement)

        db.commit()
        print(f"Successfully seeded {len(achievements)} achievements!")

    except Exception as e:
        print(f"Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_achievements()
