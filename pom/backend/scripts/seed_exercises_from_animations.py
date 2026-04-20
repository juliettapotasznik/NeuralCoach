"""
Script to automatically seed exercises from animation files.
"""
import sys
import os
import glob
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Exercise, BodyPart

# Body part keywords for auto-tagging
BODY_PART_KEYWORDS = {
    "chest": ["bench", "press", "fly", "pec"],
    "back": ["row", "pulldown", "pull", "deadlift"],
    "legs": ["squat", "lunge", "leg", "press", "calf"],
    "shoulders": ["shoulder", "lateral", "raise", "shrug"],
    "arms": ["curl", "tricep", "bicep", "kickback", "extension"],
    "core": ["crunch", "sit", "plank", "ab", "core"],
    "glutes": ["glute", "hip", "thrust", "kickback", "bridge"],
    "cardio": ["cardio", "burpee", "jump", "running", "rowing"]
}

def parse_exercise_name(filename):
    """Convert CamelCase filename to readable name."""
    # Remove .mp4 extension
    name = os.path.splitext(filename)[0]

    # Add spaces before capitals
    name = re.sub(r'([A-Z])', r' \1', name).strip()

    return name

def detect_body_parts(exercise_name):
    """Detect body parts from exercise name."""
    name_lower = exercise_name.lower()
    detected_parts = []

    for body_part, keywords in BODY_PART_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                if body_part not in detected_parts:
                    detected_parts.append(body_part)
                break

    # Default to legs if no body part detected
    if not detected_parts:
        detected_parts = ["legs"]

    return detected_parts

def seed_exercises_from_animations():
    """Seed exercises from animation files."""
    print("Seeding exercises from animation files...")
    db = SessionLocal()

    try:
        # Get all animation files
        animations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "animations")
        animation_files = glob.glob(os.path.join(animations_dir, "*.mp4"))

        print(f"Found {len(animation_files)} animation files")

        # Create body parts if they don't exist
        body_parts_data = ["chest", "back", "legs", "shoulders", "arms", "core", "glutes", "cardio"]
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

        # Process each animation file
        created_count = 0
        skipped_count = 0

        for animation_path in sorted(animation_files):
            filename = os.path.basename(animation_path)
            exercise_name = parse_exercise_name(filename)

            # Check if exercise already exists
            existing = db.query(Exercise).filter(Exercise.media_file == filename).first()
            if existing:
                print(f"  Skipping {exercise_name} (already exists)")
                skipped_count += 1
                continue

            # Detect body parts
            detected_body_parts = detect_body_parts(exercise_name)

            # Create exercise
            exercise = Exercise(
                name=exercise_name,
                media_file=filename,
                attribution="NeuralCoach Exercise Library",
                description=f"Perform {exercise_name} with proper form and control.",
                is_analyzable=True
            )

            # Add body parts
            for bp_name in detected_body_parts:
                if bp_name in body_parts:
                    exercise.body_parts.append(body_parts[bp_name])

            db.add(exercise)
            print(f"  Created: {exercise_name} ({', '.join(detected_body_parts)})")
            created_count += 1

        db.commit()
        print(f"\nSuccessfully created {created_count} exercises!")
        print(f"Skipped {skipped_count} existing exercises")

        # Verify
        total = db.query(Exercise).count()
        analyzable = db.query(Exercise).filter(Exercise.is_analyzable == True).count()
        print(f"\nTotal exercises in database: {total}")
        print(f"Analyzable exercises: {analyzable}")

    except Exception as e:
        print(f"Error seeding exercises: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_exercises_from_animations()
