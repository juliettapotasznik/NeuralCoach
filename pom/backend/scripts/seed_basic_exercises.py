"""
Script to seed basic exercises into the database.
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Exercise, BodyPart

def seed_basic_exercises():
    """Seed basic analyzable exercises into the database."""
    print("Seeding basic exercises...")
    db = SessionLocal()

    try:
        # Check if exercises already exist
        if db.query(Exercise).count() > 0:
            print("Exercises already exist in database. Skipping seed.")
            return

        # Create body parts if they don't exist
        body_parts_data = [
            "chest", "back", "legs", "shoulders", "arms", "core", "glutes", "cardio"
        ]

        body_parts = {}
        for bp_name in body_parts_data:
            bp = db.query(BodyPart).filter(BodyPart.name == bp_name).first()
            if not bp:
                bp = BodyPart(name=bp_name)
                db.add(bp)
                db.flush()
            body_parts[bp_name] = bp

        db.commit()
        print(f"Created/verified {len(body_parts)} body parts")

        # Create basic exercises
        exercises = [
            {
                "name": "squats",
                "media_file": "squats.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Stand with feet shoulder-width apart. Lower your body by bending your knees and hips, keeping your chest up. Push through your heels to return to standing.",
                "is_analyzable": True,
                "body_parts": ["legs", "glutes", "core"]
            },
            {
                "name": "biceps",
                "media_file": "biceps_curl.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Stand with dumbbells at your sides. Curl the weights up by bending your elbows, keeping your upper arms stationary. Lower back down with control.",
                "is_analyzable": True,
                "body_parts": ["arms"]
            },
            {
                "name": "pushups",
                "media_file": "pushups.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Start in a plank position. Lower your body until your chest nearly touches the floor. Push back up to starting position.",
                "is_analyzable": True,
                "body_parts": ["chest", "arms", "shoulders", "core"]
            },
            {
                "name": "lunges",
                "media_file": "lunges.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Step forward with one leg and lower your hips until both knees are bent at 90 degrees. Push back to starting position and repeat with other leg.",
                "is_analyzable": True,
                "body_parts": ["legs", "glutes"]
            },
            {
                "name": "plank",
                "media_file": "plank.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Hold a position similar to a push-up for the maximum possible time. Keep your body in a straight line from head to heels.",
                "is_analyzable": True,
                "body_parts": ["core", "shoulders"]
            },
            {
                "name": "deadlift",
                "media_file": "deadlift.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Stand with feet hip-width apart, barbell over your feet. Bend at the hips and knees to grasp the bar. Lift by extending your hips and knees, keeping the bar close to your body.",
                "is_analyzable": True,
                "body_parts": ["back", "legs", "glutes", "core"]
            },
            {
                "name": "bench press",
                "media_file": "bench_press.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Lie on a bench with feet flat on the floor. Lower the barbell to your chest, then press it back up to arm's length.",
                "is_analyzable": True,
                "body_parts": ["chest", "shoulders", "arms"]
            },
            {
                "name": "pull-ups",
                "media_file": "pullups.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Hang from a pull-up bar with palms facing away. Pull yourself up until your chin is over the bar, then lower back down with control.",
                "is_analyzable": True,
                "body_parts": ["back", "arms"]
            },
            {
                "name": "shoulder press",
                "media_file": "shoulder_press.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Hold dumbbells at shoulder height. Press the weights overhead until your arms are fully extended, then lower back down.",
                "is_analyzable": True,
                "body_parts": ["shoulders", "arms"]
            },
            {
                "name": "burpees",
                "media_file": "burpees.mp4",
                "attribution": "NeuralCoach Exercise Library",
                "description": "Start standing, drop into a squat, kick your feet back into a plank, do a push-up, jump your feet back to squat, and jump up.",
                "is_analyzable": True,
                "body_parts": ["cardio", "chest", "legs", "core"]
            }
        ]

        for ex_data in exercises:
            body_part_names = ex_data.pop("body_parts")
            exercise = Exercise(**ex_data)

            # Add body parts
            for bp_name in body_part_names:
                if bp_name in body_parts:
                    exercise.body_parts.append(body_parts[bp_name])

            db.add(exercise)

        db.commit()
        print(f"Successfully created {len(exercises)} basic exercises!")

        # Verify
        total = db.query(Exercise).count()
        analyzable = db.query(Exercise).filter(Exercise.is_analyzable == True).count()
        print(f"Total exercises in database: {total}")
        print(f"Analyzable exercises: {analyzable}")

    except Exception as e:
        print(f"Error seeding exercises: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_basic_exercises()
