import os
import json
import logging
import time
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import diet generation modules
import sys
diet_module_path = str(Path(__file__).parent.parent / "diet")
if diet_module_path not in sys.path:
    sys.path.insert(0, diet_module_path)

from UserProfile import UserProfile
from RecipeRag import RecipeRAG
from DietPlanGenerator import DietPlanGenerator
from database import get_db
from models import DietPlan
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diet", tags=["diet"])


class UserProfileRequest(BaseModel):
    age: int
    gender: str
    weight: float
    height: float
    goal: str
    activity_level: str
    diet: Optional[str] = None
    intolerances: Optional[List[str]] = None
    time_frame: str = "day"
    prefer_ingredients: Optional[List[str]] = None
    num_meals: int = 3
    macro_profile: Optional[str] = None


class DietPlanResponse(BaseModel):
    nutrition: Dict[str, Any]
    meal_plan: List[Dict[str, Any]]
    generated_at: str
    cached: bool = False


#RAG
recipes_csv_path = Path(__file__).parent.parent / "data" / "recipes_ready_for_ai.csv"
rag_system = None

def get_rag_system() -> RecipeRAG:
    global rag_system
    if rag_system is None:
        if not recipes_csv_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Recipe database not available"
            )
        logger.info(f"Initializing RAG system with recipes from: {recipes_csv_path}")
        rag_system = RecipeRAG(csv_path=str(recipes_csv_path))
    return rag_system


async def generate_diet_async(user_profile: UserProfile, rag: RecipeRAG, api_key: str) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    generator = DietPlanGenerator(rag=rag, gemini_api_key=api_key)
    result = await loop.run_in_executor(
        None,
        generator.generate_meal_plan,
        user_profile
    )
    return result


@router.get("/health", tags=["Health"])
async def health_check():
    """Check if diet generation service is healthy."""
    recipes_exists = recipes_csv_path.exists()
    api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    healthy = recipes_exists and api_key_set

    return {
        "status": "healthy" if healthy else "degraded",
        "checks": {
            "recipes_csv": recipes_exists,
            "gemini_api_key": api_key_set
        }
    }


@router.post("", response_model=DietPlanResponse, status_code=status.HTTP_200_OK)
async def generate_diet_plan(
    profile: UserProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Diet plan request received - Age: {profile.age}, Goal: {profile.goal}")

    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not set")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not configured"
            )

        # Get RAG system
        rag = get_rag_system()

        # Convert request to UserProfile
        user_profile = UserProfile(**profile.dict())

        logger.info("Starting diet generation")
        start_time = time.time()

        # Generate diet plan
        diet_plan = await generate_diet_async(user_profile, rag, gemini_api_key)

        generation_time = time.time() - start_time
        logger.info(f"Diet generation completed in {generation_time:.2f}s")

        # Deactivate old diet plans
        db.query(DietPlan).filter(
            DietPlan.user_id == current_user.id,
            DietPlan.is_active == True
        ).update({"is_active": False})

        # Save new diet plan to database
        new_diet_plan = DietPlan(
            user_id=current_user.id,
            nutrition=diet_plan.get("nutrition", {}),
            meal_plan=diet_plan.get("meal_plan", []),
            is_active=True
        )
        db.add(new_diet_plan)
        db.commit()
        db.refresh(new_diet_plan)

        response_data = {
            "nutrition": diet_plan.get("nutrition", {}),
            "meal_plan": diet_plan.get("meal_plan", []),
            "generated_at": new_diet_plan.generated_at.isoformat(),
            "cached": False
        }

        return DietPlanResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating diet plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate diet plan: {str(e)}"
        )


@router.get("/current", response_model=DietPlanResponse)
async def get_current_diet_plan(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current active diet plan."""
    diet_plan = db.query(DietPlan).filter(
        DietPlan.user_id == current_user.id,
        DietPlan.is_active == True
    ).order_by(DietPlan.generated_at.desc()).first()

    if not diet_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active diet plan found"
        )

    # Transform nutrition data to expected format
    nutrition_data = diet_plan.nutrition
    if "daily_targets" in nutrition_data:
        # Transform from stored format to API format
        daily_targets = nutrition_data["daily_targets"]
        nutrition = {
            "calories": daily_targets.get("calories", 0),
            "protein": daily_targets.get("protein_g", 0),
            "carbs": daily_targets.get("carbs_g", 0),
            "fat": daily_targets.get("fat_g", 0)
        }
    else:
        # Already in correct format or fallback
        nutrition = {
            "calories": nutrition_data.get("calories", 0),
            "protein": nutrition_data.get("protein", 0),
            "carbs": nutrition_data.get("carbs", 0),
            "fat": nutrition_data.get("fat", 0)
        }

    # Transform meal_plan data structure
    # Database format: [{"day": 1, "meals": [...]}]
    # Frontend expects: [{"meal_type": "breakfast", "recipes": [...]}]
    transformed_meal_plan = []
    if diet_plan.meal_plan and len(diet_plan.meal_plan) > 0:
        day_plan = diet_plan.meal_plan[0]  # Get first day
        if "meals" in day_plan:
            # Group meals by meal_slot
            meal_groups = {}
            for meal in day_plan["meals"]:
                meal_slot = meal.get("meal_slot", "unknown")
                if meal_slot not in meal_groups:
                    meal_groups[meal_slot] = []
                meal_groups[meal_slot].append(meal)

            # Convert to frontend format
            for meal_type, recipes in meal_groups.items():
                transformed_meal_plan.append({
                    "meal_type": meal_type,
                    "recipes": recipes
                })

    logger.info(f"Returning diet plan - nutrition: {nutrition}, meal_plan length: {len(transformed_meal_plan)}")
    return DietPlanResponse(
        nutrition=nutrition,
        meal_plan=transformed_meal_plan,
        generated_at=diet_plan.generated_at.isoformat(),
        cached=True
    )
