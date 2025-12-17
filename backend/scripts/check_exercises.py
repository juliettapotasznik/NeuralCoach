import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Exercise

db = SessionLocal()
try:
    exercises = db.query(Exercise).all()
    print(f'Total exercises in database: {len(exercises)}')
    print('\nFirst 20 exercises:')
    for i, ex in enumerate(exercises[:20], 1):
        print(f'{i}. {ex.name}')
finally:
    db.close()
