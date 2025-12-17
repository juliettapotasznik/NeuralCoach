import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Get DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

# Fix for RDS SSL if needed (same logic as in database.py)
if "rds.amazonaws.com" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)

def seed_exercises():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(script_dir, "exercises_database.sql")
    
    if not os.path.exists(sql_file_path):
        print(f"Error: {sql_file_path} not found!")
        return

    print("Reading SQL file...")
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split commands (simple split by semicolon might be fragile for complex SQL, 
    # but usually works for insert dumps)
    commands = sql_content.split(';')

    with engine.connect() as connection:
        print("Executing SQL commands...")
        count = 0
        for command in commands:
            command = command.strip()
            if command:
                try:
                    connection.execute(text(command))
                    count += 1
                except Exception as e:
                    print(f"Error executing command: {command[:50]}...")
                    print(e)
        
        connection.commit()
        print(f"Successfully executed {count} commands.")
        
        # Enable analyzable exercises
        enable_analyzable_exercises(connection)
        
        print("Database populated with exercises!")

def enable_analyzable_exercises(connection):
    """Sets is_analyzable=True for supported exercises"""
    print("Enabling analyzable exercises...")
    
    exercises_to_enable = [
        "Archer Push-ups", "Bench Press", "Plank", "Push-ups", "Squats", "Lunges", 
        "Bicep Curls", "Deadlift", "Shoulder Press", "Pull-ups", "Dips", "Leg Raise", 
        "Sit-ups", "Burpees", "Mountain Climbers", "Jumping Jacks", "High Knees", 
        "Butt Kicks", "Side Plank", "Russian Twists", "Bicycle Crunches", "Leg Press", 
        "Lat Pulldown", "Seated Row", "Face Pull", "Tricep Extensions", "Hammer Curls", 
        "Lateral Raises", "Front Raises", "Reverse Fly", "Chest Fly", "Incline Bench Press", 
        "Decline Bench Press", "Overhead Press", "Arnold Press", "Upright Row", "Shrugs", 
        "Calf Raises", "Leg Curls", "Leg Extensions", "Hip Thrust", "Glute Bridge", 
        "Bulgarian Split Squat", "Sumo Squat", "Goblet Squat", "Front Squat", "Box Squat", 
        "Hack Squat", "Romanian Deadlift", "Stiff Leg Deadlift", "Good Morning", 
        "Hyperextension", "Reverse Hyperextension", "Hanging Leg Raise", "Ab Wheel Rollout", 
        "Cable Crunch", "Woodchopper", "Pallof Press", "Farmer's Walk", "Suitcase Carry", 
        "Clean and Jerk", "Snatch", "Kettlebell Swing", "Turkish Get-up", "Box Jump", 
        "Step-up", "Lunge Jump", "Squat Jump", "Broad Jump", "Single Leg Deadlift", 
        "Pistol Squat", "Sissy Squat", "Nordic Hamstring Curl", "Glute Ham Raise", 
        "Reverse Lunge", "Walking Lunge", "Curtsy Lunge", "Side Lunge", "Cossack Squat", 
        "Zercher Squat", "Overhead Squat", "Thruster", "Wall Ball", "Medicine Ball Slam", 
        "Battle Ropes", "Sled Push", "Sled Pull", "Tire Flip", "Hammer Strike", "Rope Climb", 
        "Muscle-up", "Handstand Push-up", "Planache", "Front Lever", "Back Lever", 
        "Human Flag", "L-Sit", "V-Sit", "Dragon Flag"
    ]

    count = 0
    for ex_name in exercises_to_enable:
        # Use ILIKE for case-insensitive partial match
        query = text("UPDATE exercises SET is_analyzable = TRUE WHERE name ILIKE :pattern")
        
        search_term = ex_name
        if ex_name == "Shoulder Press":
            search_term = "Shoulder%Press"
        
        # Handle plural/singular mismatch (e.g. Squats -> Squat)
        if ex_name.endswith("s") and ex_name not in [
            "Bench Press", "Shoulder Press", "Overhead Press", "Pallof Press", 
            "Sled Press", "Leg Press"
        ]:
             search_term = ex_name[:-1]

        pattern = f"%{search_term}%"
        result = connection.execute(query, {"pattern": pattern})
        count += result.rowcount

    connection.commit()
    print(f"Enabled {count} exercises as analyzable.")

if __name__ == "__main__":
    seed_exercises()
