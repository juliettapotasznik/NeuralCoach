from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator

from database import get_db
from models import User, Goal, Achievement, UserAchievement, AnalysisHistory, WorkoutPlan, CompletedExercise, DietPlan, CompletedMeal
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])




class UserStatsResponse(BaseModel):
    username: str
    level: int
    points: int
    current_streak: int
    workouts_this_week: int
    workouts_this_month: int
    total_workouts: int

    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool
    unlocked_at: Optional[datetime]
    progress: int
    requirement: int

    class Config:
        from_attributes = True


class GoalResponse(BaseModel):
    id: int
    title: str
    target_value: int
    current_value: int
    unit: str
    deadline: Optional[datetime]
    completed: bool
    completed_at: Optional[datetime]
    progress_percentage: float

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    target_value: int
    unit: str
    deadline: Optional[datetime] = None

    @field_validator('deadline', mode='before')
    @classmethod
    def validate_deadline(cls, v):
        if v == "" or v is None:
            return None
        # If it's a date string (YYYY-MM-DD), convert to datetime
        if isinstance(v, str) and len(v) == 10:
            return datetime.strptime(v, '%Y-%m-%d')
        return v


class GoalUpdate(BaseModel):
    current_value: int


class RecentWorkoutResponse(BaseModel):
    id: int
    exercise_name: str
    avg_rating: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutPlanCreate(BaseModel):
    plan_name: str
    exercises: List[dict]  # List of exercise objects


class WorkoutPlanResponse(BaseModel):
    id: int
    plan_name: str
    exercises: List[dict]
    generated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True




@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    total_workouts = db.query(AnalysisHistory).filter(
        AnalysisHistory.user_id == current_user.id
    ).count()

    return UserStatsResponse(
        username=current_user.username,
        level=current_user.level,
        points=current_user.points,
        current_streak=current_user.current_streak,
        workouts_this_week=current_user.workouts_this_week,
        workouts_this_month=current_user.workouts_this_month,
        total_workouts=total_workouts
    )



@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all achievements with user's unlock status."""
    achievements = db.query(Achievement).all()
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).all()

    user_achievement_map = {ua.achievement_id: ua for ua in user_achievements}

    result = []
    for achievement in achievements:
        user_ach = user_achievement_map.get(achievement.id)

        # Calculate progress based on category
        progress = 0
        if achievement.category == "workout":
            progress = db.query(AnalysisHistory).filter(
                AnalysisHistory.user_id == current_user.id
            ).count()
        elif achievement.category == "streak":
            progress = current_user.current_streak
        elif achievement.category == "social":
            from models import Friendship
            progress = db.query(Friendship).filter(
                Friendship.user_id == current_user.id,
                Friendship.status == "accepted"
            ).count()

        # Auto-unlock achievement if progress meets requirement
        if progress >= achievement.requirement and user_ach is None:
            user_ach = UserAchievement(
                user_id=current_user.id,
                achievement_id=achievement.id,
                unlocked_at=datetime.now(timezone.utc)
            )
            db.add(user_ach)
            db.commit()
            db.refresh(user_ach)

        result.append(AchievementResponse(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            category=achievement.category,
            unlocked=user_ach is not None,
            unlocked_at=user_ach.unlocked_at if user_ach else None,
            progress=min(progress, achievement.requirement),
            requirement=achievement.requirement
        ))

    return result



@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's goals."""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()

    return [
        GoalResponse(
            id=goal.id,
            title=goal.title,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            deadline=goal.deadline,
            completed=goal.completed,
            completed_at=goal.completed_at,
            progress_percentage=(goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        )
        for goal in goals
    ]


@router.post("/goals/create")
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    goal = Goal(
        user_id=current_user.id,
        title=goal_data.title,
        target_value=goal_data.target_value,
        unit=goal_data.unit,
        deadline=goal_data.deadline
    )
    db.add(goal)

    # Award points for creating a goal
    POINTS_PER_GOAL = 10
    current_user.points += POINTS_PER_GOAL

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()
    db.refresh(goal)

    return {
        "message": "Goal created successfully",
        "goal_id": goal.id,
        "points_earned": POINTS_PER_GOAL,
        "total_points": current_user.points,
        "level": current_user.level
    }


@router.put("/goals/{goal_id}")
async def update_goal_progress(
    goal_id: int,
    update_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.current_value = update_data.current_value

    # Check if goal is completed
    if goal.current_value >= goal.target_value and not goal.completed:
        goal.completed = True
        goal.completed_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Goal updated successfully"}


@router.post("/goals/{goal_id}/complete")
async def complete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a goal as completed."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.completed:
        raise HTTPException(status_code=400, detail="Goal already completed")

    # Mark as completed
    goal.completed = True
    goal.completed_at = datetime.now(timezone.utc)
    goal.current_value = goal.target_value  # Set to 100%

    # Award points for completing a goal
    POINTS_PER_COMPLETED_GOAL = 50
    current_user.points += POINTS_PER_COMPLETED_GOAL

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()

    return {
        "message": "Goal completed successfully",
        "points_earned": POINTS_PER_COMPLETED_GOAL,
        "total_points": current_user.points,
        "level": current_user.level
    }


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()

    return {"message": "Goal deleted successfully"}




@router.get("/recent-workouts", response_model=List[RecentWorkoutResponse])
async def get_recent_workouts(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    workouts = db.query(AnalysisHistory).filter(
        AnalysisHistory.user_id == current_user.id
    ).order_by(desc(AnalysisHistory.created_at)).limit(limit).all()

    return [
        RecentWorkoutResponse(
            id=workout.id,
            exercise_name=workout.exercise_name,
            avg_rating=workout.avg_rating,
            created_at=workout.created_at
        )
        for workout in workouts
    ]


# Workout Plan Endpoints

@router.post("/workout-plans/create")
async def create_workout_plan(
    plan_data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workout plan for the user."""
    # Deactivate old workout plans
    db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).update({"is_active": False})

    # Create new workout plan
    workout_plan = WorkoutPlan(
        user_id=current_user.id,
        plan_name=plan_data.plan_name,
        exercises=plan_data.exercises,
        is_active=True
    )
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)

    return {"message": "Workout plan created successfully", "plan_id": workout_plan.id}


@router.get("/workout-plans/current", response_model=WorkoutPlanResponse)
async def get_current_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current active workout plan."""
    workout_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).order_by(desc(WorkoutPlan.generated_at)).first()

    if not workout_plan:
        raise HTTPException(
            status_code=404,
            detail="No active workout plan found"
        )

    return WorkoutPlanResponse(
        id=workout_plan.id,
        plan_name=workout_plan.plan_name,
        exercises=workout_plan.exercises,
        generated_at=workout_plan.generated_at,
        is_active=workout_plan.is_active
    )


@router.get("/workout-plans", response_model=List[WorkoutPlanResponse])
async def get_all_workout_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workout plans for the user."""
    workout_plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id
    ).order_by(desc(WorkoutPlan.generated_at)).all()

    return [
        WorkoutPlanResponse(
            id=plan.id,
            plan_name=plan.plan_name,
            exercises=plan.exercises,
            generated_at=plan.generated_at,
            is_active=plan.is_active
        )
        for plan in workout_plans
    ]


@router.put("/workout-plans/{plan_id}/activate")
async def activate_workout_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a workout plan as active."""
    # Check if plan exists and belongs to user
    workout_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    # Deactivate all other plans
    db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).update({"is_active": False})

    # Activate this plan
    workout_plan.is_active = True
    db.commit()

    return {"message": "Workout plan activated successfully"}


@router.delete("/workout-plans/{plan_id}")
async def delete_workout_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workout plan."""
    workout_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    db.delete(workout_plan)
    db.commit()

    return {"message": "Workout plan deleted successfully"}


# Exercise Completion Endpoints

class CompleteExerciseRequest(BaseModel):
    exercise_index: int


@router.post("/workout-plans/{plan_id}/exercises/complete")
async def mark_exercise_complete(
    plan_id: int,
    request: CompleteExerciseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an exercise in the workout plan as completed."""
    # Verify workout plan exists and belongs to user
    workout_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    # Check if already completed today
    existing = db.query(CompletedExercise).filter(
        CompletedExercise.user_id == current_user.id,
        CompletedExercise.workout_plan_id == plan_id,
        CompletedExercise.exercise_index == request.exercise_index,
        func.date(CompletedExercise.completed_at) == datetime.now(timezone.utc).date()
    ).first()

    if existing:
        return {"message": "Exercise already marked as completed today"}

    # Create completion record
    completed = CompletedExercise(
        user_id=current_user.id,
        workout_plan_id=plan_id,
        exercise_index=request.exercise_index
    )
    db.add(completed)

    # Award points for completing exercise
    POINTS_PER_EXERCISE = 10
    current_user.points += POINTS_PER_EXERCISE

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()

    return {
        "message": "Exercise marked as completed",
        "points_earned": POINTS_PER_EXERCISE,
        "total_points": current_user.points,
        "level": current_user.level
    }


@router.get("/workout-plans/{plan_id}/completed-exercises")
async def get_completed_exercises(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get completed exercises for today for a specific workout plan."""
    completed = db.query(CompletedExercise).filter(
        CompletedExercise.user_id == current_user.id,
        CompletedExercise.workout_plan_id == plan_id,
        func.date(CompletedExercise.completed_at) == datetime.now(timezone.utc).date()
    ).all()

    return {"completed_indices": [c.exercise_index for c in completed]}


# Meal Completion Endpoints

class CompleteMealRequest(BaseModel):
    meal_type: str
    recipe_index: int


@router.post("/diet-plans/current/meals/complete")
async def mark_meal_complete(
    request: CompleteMealRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a meal in the current diet plan as completed."""
    # Get current active diet plan
    diet_plan = db.query(DietPlan).filter(
        DietPlan.user_id == current_user.id,
        DietPlan.is_active == True
    ).order_by(desc(DietPlan.generated_at)).first()

    if not diet_plan:
        raise HTTPException(status_code=404, detail="No active diet plan found")

    # Check if already completed today
    existing = db.query(CompletedMeal).filter(
        CompletedMeal.user_id == current_user.id,
        CompletedMeal.diet_plan_id == diet_plan.id,
        CompletedMeal.meal_type == request.meal_type,
        CompletedMeal.recipe_index == request.recipe_index,
        func.date(CompletedMeal.completed_at) == datetime.now(timezone.utc).date()
    ).first()

    if existing:
        return {"message": "Meal already marked as completed today"}

    # Create completion record
    completed = CompletedMeal(
        user_id=current_user.id,
        diet_plan_id=diet_plan.id,
        meal_type=request.meal_type,
        recipe_index=request.recipe_index
    )
    db.add(completed)

    # Award points for completing meal
    POINTS_PER_MEAL = 15
    current_user.points += POINTS_PER_MEAL

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()

    return {
        "message": "Meal marked as completed",
        "points_earned": POINTS_PER_MEAL,
        "total_points": current_user.points,
        "level": current_user.level
    }


@router.get("/diet-plans/current/completed-meals")
async def get_completed_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get completed meals for today."""
    # Get current active diet plan
    diet_plan = db.query(DietPlan).filter(
        DietPlan.user_id == current_user.id,
        DietPlan.is_active == True
    ).order_by(desc(DietPlan.generated_at)).first()

    if not diet_plan:
        return {"completed_meals": [], "nutrition_consumed": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}}

    # Get completed meals for today
    completed = db.query(CompletedMeal).filter(
        CompletedMeal.user_id == current_user.id,
        CompletedMeal.diet_plan_id == diet_plan.id,
        func.date(CompletedMeal.completed_at) == datetime.now(timezone.utc).date()
    ).all()

    # Calculate nutrition consumed
    nutrition_consumed = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for meal in completed:
        # Find the meal in the diet plan
        # Database format: [{"day": 1, "meals": [{"meal_slot": "breakfast", ...}]}]
        if diet_plan.meal_plan and len(diet_plan.meal_plan) > 0:
            day_plan = diet_plan.meal_plan[0]  # Get first day
            if "meals" in day_plan:
                meals_list = day_plan["meals"]
                # Find meals that match the meal_type (stored as meal_slot in DB)
                matching_meals = [m for m in meals_list if m.get("meal_slot") == meal.meal_type]

                if meal.recipe_index < len(matching_meals):
                    recipe = matching_meals[meal.recipe_index]
                    # Support multiple field naming conventions
                    nutrition_consumed["calories"] += recipe.get("calories", recipe.get("calories_per_serving", 0))
                    nutrition_consumed["protein"] += recipe.get("protein", recipe.get("protein_g", recipe.get("protein_per_serving", 0)))
                    nutrition_consumed["carbs"] += recipe.get("carbs", recipe.get("carbs_g", recipe.get("carbs_per_serving", 0)))
                    nutrition_consumed["fat"] += recipe.get("fat", recipe.get("fat_g", recipe.get("fat_per_serving", 0)))

    return {
        "completed_meals": [
            {
                "meal_type": c.meal_type,
                "recipe_index": c.recipe_index,
                "completed_at": c.completed_at
            }
            for c in completed
        ],
        "nutrition_consumed": nutrition_consumed
    }
