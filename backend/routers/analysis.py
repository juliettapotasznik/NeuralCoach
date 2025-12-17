"""
Analysis history endpoints - get user's analysis history.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from database import get_db
from models import User, AnalysisHistory
from schemas import AnalysisHistoryResponse, AnalysisHistoryList
from auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/history", response_model=AnalysisHistoryList)
async def get_analysis_history(
    limit: int = Query(default=10, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    exercise_name: Optional[str] = Query(default=None, description="Filter by exercise name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's analysis history with pagination.

    Args:
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip
        exercise_name: Optional filter by exercise name
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of analysis history records with total count
    """
    import json
    
    # Build query
    query = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id)

    # Apply exercise filter if provided
    if exercise_name:
        query = query.filter(AnalysisHistory.exercise_name == exercise_name)

    # Get total count
    total = query.count()

    # Get paginated results ordered by most recent first
    analyses = query.order_by(desc(AnalysisHistory.created_at)).offset(offset).limit(limit).all()

    # Deserialize JSON strings to dicts if needed
    for analysis in analyses:
        if analysis.joint_ratings and isinstance(analysis.joint_ratings, str):
            analysis.joint_ratings = json.loads(analysis.joint_ratings)

    return {
        "total": total,
        "analyses": analyses
    }


@router.get("/history/{analysis_id}", response_model=AnalysisHistoryResponse)
async def get_analysis_by_id(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific analysis by ID.

    Args:
        analysis_id: Analysis record ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Analysis history record

    Raises:
        HTTPException: If analysis not found or doesn't belong to user
    """
    analysis = db.query(AnalysisHistory).filter(
        AnalysisHistory.id == analysis_id,
        AnalysisHistory.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete specific analysis by ID.

    Args:
        analysis_id: Analysis record ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If analysis not found or doesn't belong to user
    """
    analysis = db.query(AnalysisHistory).filter(
        AnalysisHistory.id == analysis_id,
        AnalysisHistory.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    try:
        db.delete(analysis)
        db.commit()
    except Exception as e:
        logger.error(f"Delete analysis error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis. Please try again."
        )

    return None
