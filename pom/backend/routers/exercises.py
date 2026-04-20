"""
Exercise endpoints - get exercise library.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import os
import glob

from database import get_db
from models import Exercise, BodyPart
from schemas import ExerciseResponse, ExerciseListResponse

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

# Path to animations directory
ANIMATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "animations")


@router.get("/list", response_model=ExerciseListResponse)
async def get_exercise_list(
    body_part: Optional[str] = Query(default=None, description="Filter by body part name"),
    analyzable: Optional[bool] = Query(default=None, description="Filter by analyzable status"),
    limit: int = Query(default=100, ge=1, le=500, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    Get list of exercises with their details.

    Args:
    - name: Exercise name
    - description: Exercise instructions
    - media_file: Path to animation/video file
    - body_part: Associated body part/muscle group
    - attribution: Attribution text for the media

    Args:
        body_part: Optional filter by body part name (e.g., "Back", "Legs", "Chest")
        analyzable: Optional filter by analyzable status
        limit: Maximum number of results to return (1-500)
        offset: Number of results to skip
        db: Database session

    Returns:
        List of exercises with total count
    """
    # Build query with eager loading of body_parts
    query = db.query(Exercise).options(joinedload(Exercise.body_parts))

    # Apply body part filter if provided
    if body_part:
        query = query.join(Exercise.body_parts).filter(BodyPart.name.ilike(f"%{body_part}%"))

    # Apply analyzable filter if provided
    if analyzable is not None:
        query = query.filter(Exercise.is_analyzable == analyzable)

    # Get total count
    if body_part:
        total = query.distinct().count()
    else:
        total = query.count()

    # Get paginated results ordered by name
    if body_part:
        exercises = query.distinct().order_by(Exercise.name).offset(offset).limit(limit).all()
    else:
        exercises = query.order_by(Exercise.name).offset(offset).limit(limit).all()

    return {
        "total": total,
        "exercises": exercises
    }


@router.get("/catalog", response_model=ExerciseListResponse)
async def get_exercise_catalog(
    search: Optional[str] = Query(default=None, description="Search by exercise name"),
    db: Session = Depends(get_db)
):
    """
    Get exercises that have animation files available.

    Returns exercises with matching animation files from the backend/animations directory.
    Only returns exercises where an animation file exists.

    Args:
        search: Optional search term to filter by exercise name
        db: Database session

    Returns:
        List of exercises with animations
    """
    # Get all animation files
    if not os.path.exists(ANIMATIONS_DIR):
        return {"total": 0, "exercises": []}

    animation_files = glob.glob(os.path.join(ANIMATIONS_DIR, "*.mp4"))
    animation_names = {os.path.splitext(os.path.basename(f))[0] for f in animation_files}

    # Build base query
    query = db.query(Exercise).options(joinedload(Exercise.body_parts))

    # Filter by animation availability - match exercise names with animation filenames
    # Remove spaces and special characters for matching
    exercises_with_animations = []
    all_exercises = query.all()

    for exercise in all_exercises:
        # Create potential animation filename from exercise name
        clean_name = exercise.name.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Check if any animation filename matches
        if any(clean_name.lower() in anim_name.lower() or anim_name.lower() in clean_name.lower() for anim_name in animation_names):
            # Find the matching animation
            for anim_name in animation_names:
                if clean_name.lower() in anim_name.lower() or anim_name.lower() in clean_name.lower():
                    exercise.media_file = f"{anim_name}.mp4"
                    break
            exercises_with_animations.append(exercise)

    # Apply search filter if provided
    if search:
        exercises_with_animations = [
            ex for ex in exercises_with_animations
            if search.lower() in ex.name.lower()
        ]

    return {
        "total": len(exercises_with_animations),
        "exercises": exercises_with_animations
    }


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise_by_id(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific exercise by ID.

    Args:
        exercise_id: Exercise ID
        db: Database session

    Returns:
        Exercise details

    Raises:
        HTTPException: If exercise not found
    """
    exercise = db.query(Exercise).options(joinedload(Exercise.body_parts)).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    return exercise

