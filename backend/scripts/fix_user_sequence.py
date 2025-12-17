"""
Fix the users table ID sequence to prevent duplicate key errors.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sqlalchemy import text


def fix_user_sequence():
    """Fix the users table ID sequence by setting it to max(id) + 1"""
    db = SessionLocal()
    try:
        # Get the maximum ID from users table
        result = db.execute(text("SELECT MAX(id) FROM users;"))
        max_id = result.scalar()

        if max_id is None:
            print("No users found in database. Sequence is fine.")
            return

        print(f"Maximum user ID: {max_id}")

        # Set the sequence to max_id + 1
        next_id = max_id + 1
        db.execute(text(f"SELECT setval('users_id_seq', {next_id}, false);"))
        db.commit()

        print(f"[SUCCESS] Successfully set users_id_seq to {next_id}")

        # Verify the fix
        result = db.execute(text("SELECT last_value FROM users_id_seq;"))
        current_val = result.scalar()
        print(f"Current sequence value: {current_val}")

    except Exception as e:
        print(f"[ERROR] Error fixing sequence: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_user_sequence()
