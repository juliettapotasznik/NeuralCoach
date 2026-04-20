"""
FastAPI Gateway Service for RepRight Exercise Analysis
Integrates OpenVINO pose extraction and LSTM Autoencoder analysis.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import httpx
import logging
import time
import base64
import uuid
import asyncio
import magic
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from services import openvino_client, autoencoder_client
from database import init_db, get_db
from models import User, AnalysisHistory, Exercise
from auth import get_current_user_optional

from routers import users, analysis, diet, community, dashboard, exercises

# Load environment variables (don't override Docker env vars)
load_dotenv(override=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NeuralCoach Gateway API",
    description="Video processing backend for exercise analysis with user management",
    version="2.0.0"
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Enable CORS for frontend - must be added FIRST (executed LAST)
# Security: Restrict origins in production
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js Web Local
    "http://localhost:8002",  # Swagger UI
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # Allow all headers for development
    expose_headers=["*"],
)

# Security: Trusted Host Middleware (prevents Host Header Injection)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "neural-coach.com", "*.neural-coach.com", "testserver"]
)

# Security: HSTS Middleware (Force HTTPS)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Only add security headers if not in development
    if request.url.hostname not in ["localhost", "127.0.0.1"]:
        # HSTS (1 year, include subdomains) - Only effective on HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # X-Content-Type-Options (Prevent MIME sniffing)
    response.headers["X-Content-Type-Options"] = "nosniff"
    # X-Frame-Options (Prevent Clickjacking) - relaxed for development
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

# Include routers
app.include_router(users.router)
app.include_router(analysis.router)

app.include_router(diet.router)
app.include_router(community.router)
app.include_router(dashboard.router)

app.include_router(exercises.router)


# Create uploads directory and mount static files
uploads_dir = Path("/app/uploads/profile_pictures")
uploads_dir.mkdir(parents=True, exist_ok=True)

# Create processed videos directory
processed_videos_dir = Path("/app/uploads/processed_videos")
processed_videos_dir.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# Mount animations/overlays directory
# Use relative path for local development, absolute for Docker
import os

if os.path.exists("../ai/user_videos_skel"):
    # Running locally (development) - backend is run from backend/ directory
    overlays_dir = Path("../ai/user_videos_skel").resolve()
elif os.path.exists("./ai/user_videos_skel"):
    # Running from root directory
    overlays_dir = Path("./ai/user_videos_skel").resolve()
else:
    # Running in Docker
    overlays_dir = Path("/app/user_videos_skel")

overlays_dir.mkdir(parents=True, exist_ok=True)
app.mount("/overlays", StaticFiles(directory=str(overlays_dir)), name="overlays")
logger.info(f"Mounted overlays directory: {overlays_dir}")

# Mount animations directory
# Support both Docker (/app/animations) and local development (./animations)
animations_dir = Path("/app/animations") if Path("/app/animations").exists() else Path(__file__).parent / "animations"
if animations_dir.exists():
    app.mount("/animations", StaticFiles(directory=str(animations_dir)), name="animations")
    logger.info(f"Mounted animations directory: {animations_dir}")
else:
    logger.warning("Animations directory not found at %s", animations_dir)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        raise# File validation constants
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "application/octet-stream"} # octet-stream sometimes happens with avi
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


async def validate_video_file(file: UploadFile) -> None:
    """
    Validate uploaded video file.

    Args:
        file: Uploaded file object

    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file content using magic numbers
    # Read first 2KB to determine type
    await file.seek(0)
    header = await file.read(2048)
    await file.seek(0) # Reset cursor
    
    mime_type = magic.from_buffer(header, mime=True)
    logger.info(f"File {file.filename} has MIME type: {mime_type}")
    
    if mime_type not in ALLOWED_MIME_TYPES:
        # Relaxed check for some containers that might be detected generically
        if not mime_type.startswith("video/"):
             raise HTTPException(
                status_code=400,
                detail=f"Invalid file content. Detected type: {mime_type}"
            )


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": "NeuralCoach Gateway API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "register": "POST /api/users/register",
            "login": "POST /api/users/login",
            "profile": "GET /api/users/me",
            "delete_account": "DELETE /api/users/me",
            "analysis_history": "GET /api/analysis/history",
            "exercise_list": "GET /api/exercises/list",
            "analyze_exercise": "POST /analyze_exercise",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze_exercise")
async def analyze_exercise(
    file: UploadFile = File(..., description="Video file (MP4, MOV, or AVI)"),
    exercise_name: str = Form(..., description="Name of the exercise (e.g., biceps, squats)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze exercise video for form and technique.

    This endpoint chains two AI services:
    1. OpenVINO service: Extracts pose data from video
    2. LSTM Autoencoder: Analyzes pose data and generates feedback

    If user is authenticated, the analysis is saved to their history.

    Args:
        file: Video file upload
        exercise_name: Name of the exercise being performed
        current_user: Current authenticated user (optional)
        db: Database session

    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - feedback: Generated coaching feedback
        - joint_ratings: Per-joint performance scores (0-100)
        - avg_rating: Average rating across all joints
        - processing_time: Total processing time in seconds
        - analysis_id: ID of saved analysis (if user is authenticated)

    Raises:
        HTTPException: If validation fails or services are unavailable
    """
    start_time = time.time()

    try:
        # Validate file
        await validate_video_file(file)
        
        # Validate exercise_name against database
        exercise = db.query(Exercise).filter(
            Exercise.name == exercise_name,
            Exercise.is_analyzable == True
        ).first()

        if not exercise:
            logger.warning(f"Invalid exercise requested: {exercise_name}")
            raise HTTPException(
                status_code=400,
                detail="Invalid exercise selected or exercise not available for analysis."
            )
        
        logger.info("Processing video: %s for exercise: %s", file.filename, exercise.name)
        
        # Read file content
        video_content = await file.read()

        # Step 1: Process video with OpenVINO service
        try:
            openvino_response = await openvino_client.process_video(
                video_file=video_content,
                filename=file.filename,
                exercise_name=exercise_name
            )
            csv_base64 = openvino_response.get("csv_base64")
            video_base64 = openvino_response.get("video_base64")
            video_path = openvino_response.get("video_path")

            if not csv_base64:
                raise HTTPException(
                    status_code=500,
                    detail="OpenVINO service did not return CSV data"
                )

            logger.info(f"Received CSV data from OpenVINO: {len(csv_base64)} characters")

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="OpenVINO service timeout - video processing took too long"
            )
        except httpx.RequestError as e:
            logger.error(f"OpenVINO service unavailable: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again later."
            )

        # Step 2: Analyze CSV with LSTM Autoencoder service
        try:
            # video_path is used for overlay generation (skeleton visualization)
            autoencoder_response = await autoencoder_client.analyze_csv(
                csv_base64=csv_base64,
                exercise_name=exercise_name,
                video_path=video_path
            )
            logger.info("Autoencoder response keys: %s", list(autoencoder_response.keys()))
            logger.info("Autoencoder overlay_video_path: %s", autoencoder_response.get("overlay_video_path"))

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Analysis timed out. Please try again later."
            )
        except httpx.RequestError as e:
            logger.error(f"Autoencoder service unavailable: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again later."
            )
        # Calculate total processing time
        processing_time = time.time() - start_time

        # Build unified response
        response = {
            "status": "success",
            "feedback": autoencoder_response.get("feedback", "No feedback generated"),
            "processing_time": round(processing_time, 2)
        }

        # Handle overlay video
        overlay_video_path = autoencoder_response.get("overlay_video_path")
        if overlay_video_path:
            try:
                filename = Path(overlay_video_path).name
                response["overlay_video_url"] = f"/overlays/{filename}"
                # Prefer overlay video as the main processed video
                response["processed_video_url"] = f"/overlays/{filename}"
                logger.info("Overlay video available at %s", response['overlay_video_url'])
            except Exception as e:
                logger.error("Failed to process overlay video path: %s", e)

        # Handle processed video
        if video_base64:
            try:
                # Generate unique filename
                processed_filename = f"processed_{uuid.uuid4()}.mp4"
                processed_file_path = processed_videos_dir / processed_filename
                
                # Decode and save video
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: open(processed_file_path, "wb").write(base64.b64decode(video_base64)))
                
                # Add URL to response (assuming /uploads mount)
                # Note: In production, use full URL or relative path handled by frontend
                if "processed_video_url" not in response:
                    response["processed_video_url"] = f"/uploads/processed_videos/{processed_filename}"
                
                logger.info("Saved processed video to %s", processed_file_path)
            except Exception as e:
                logger.error("Failed to save processed video: %s", e)

        # Add optional fields if present
        # Add joint ratings (per-joint scores 0-100)
        # Add joint ratings (per-joint scores 0-100)
        if "joint_ratings" in autoencoder_response:
            response["joint_ratings"] = autoencoder_response["joint_ratings"]

        # Add average rating
        if "avg_rating" in autoencoder_response:
            response["avg_rating"] = autoencoder_response["avg_rating"]

        # Save to analysis history if user is authenticated
        if current_user:
            logger.info("User authenticated: %s (ID: %s)", current_user.username, current_user.id)
            try:
                # Convert avg_rating from string "94/100" to float 94.0
                avg_rating_value = None
                if "avg_rating" in autoencoder_response:
                    avg_rating_str = autoencoder_response["avg_rating"]
                    if isinstance(avg_rating_str, str) and "/" in avg_rating_str:
                        # Extract number from "94/100" format
                        avg_rating_value = float(avg_rating_str.split("/")[0])
                    elif isinstance(avg_rating_str, (int, float)):
                        avg_rating_value = float(avg_rating_str)
                
                # Keep joint_ratings as dict (SQLAlchemy JSON column handles serialization)
                joint_ratings_data = autoencoder_response.get("joint_ratings")
                
                analysis_record = AnalysisHistory(
                    user_id=current_user.id,
                    exercise_name=exercise.name,
                    video_filename=file.filename,
                    feedback=response.get("feedback"),
                    avg_rating=avg_rating_value,
                    joint_ratings=joint_ratings_data,
                    processing_time=processing_time
                )
                db.add(analysis_record)
                db.commit()
                db.refresh(analysis_record)

                response["analysis_id"] = analysis_record.id
                logger.info("Saved analysis to history with ID: %s for user %s", analysis_record.id, current_user.username)
            except Exception as e:
                logger.error("Failed to save analysis to history: %s", e, exc_info=True)
                db.rollback()
                # Don't fail the request if history save fails
        else:
            logger.warning("No authenticated user - analysis will not be saved to history")

        logger.info("Successfully processed video in %.2fs", processing_time)
        logger.info("Response overlay_video_url: %s", response.get("overlay_video_url"))
        logger.info("Response processed_video_url: %s", response.get("processed_video_url"))
        logger.info("Full response keys: %s", list(response.keys()))
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later."
        )


if __name__ == "__main__":
    import uvicorn
    # Increase timeouts for long-running video processing
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        timeout_keep_alive=300,  # 5 minutes
        timeout_graceful_shutdown=30
    )
