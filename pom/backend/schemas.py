"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field
from typing import Optional, List, Dict, Any
from datetime import datetime
import os


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_verified: bool
    profile_picture: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


# Analysis History Schemas
class AnalysisHistoryBase(BaseModel):
    """Base analysis history schema."""
    exercise_name: str
    video_filename: Optional[str] = None
    feedback: Optional[str] = None
    avg_rating: Optional[float] = None
    joint_ratings: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None


class AnalysisHistoryCreate(AnalysisHistoryBase):
    """Schema for creating analysis history."""
    pass


class AnalysisHistoryResponse(AnalysisHistoryBase):
    """Schema for analysis history response."""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryList(BaseModel):
    """Schema for list of analysis history."""
    total: int
    analyses: List[AnalysisHistoryResponse]


# Email verification schemas
class EmailVerifyRequest(BaseModel):
    """Schema for email verification request."""
    token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str


class BodyPartResponse(BaseModel):
    """Schema for body part response."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExerciseResponse(BaseModel):
    """Schema for exercise response."""
    id: int
    name: str
    media_file: str
    attribution: str
    body_parts: List[BodyPartResponse]
    description: str
    is_analyzable: bool = False

    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def media_url(self) -> str:
        """Full URL to animation file."""
        base_url = os.getenv("API_BASE_URL", "http://localhost:8002")
        return f"{base_url}/animations/{self.media_file}"


class ExerciseListResponse(BaseModel):
    """Schema for list of exercises."""
    total: int
    exercises: List[ExerciseResponse]
