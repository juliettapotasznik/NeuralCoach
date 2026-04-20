"""
User management endpoints - registration, login, profile, delete account, email verification, password reset.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import os
import magic
import logging

from database import get_db
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    EmailVerifyRequest, PasswordResetRequest, PasswordResetConfirm,
    PasswordChange, MessageResponse
)
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    generate_verification_token,
    generate_reset_token,
    verify_password
)
from email_config import (
    send_verification_email,
    send_password_reset_email,
    send_password_changed_email
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user and send verification email.

    Args:
        user_data: User registration data (email, username, password)
        background_tasks: Background tasks for sending email
        db: Database session

    Returns:
        Created user data

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username or email already exists (case-insensitive for email)
    existing_user = db.query(User).filter(
        (func.lower(User.username) == user_data.username.lower()) | 
        (func.lower(User.email) == user_data.email.lower())
    ).first()

    if existing_user:
        if existing_user.username.lower() == user_data.username.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    hashed_password = get_password_hash(user_data.password)
    verification_token = generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    new_user = User(
        email=user_data.email.lower(),  # Always save email in lowercase
        username=user_data.username,
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=verification_expires
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            new_user.username,
            verification_token
        )

        return new_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed. This email or username may already be registered."
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )


@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT access token.

    Args:
        user_data: Login credentials (username/email and password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid or email not verified
    """
    logger.info(f"Login attempt for username: {user_data.username}")
    user = authenticate_user(db, user_data.username, user_data.password)

    if not user:
        logger.warning(f"Failed login attempt for username: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user profile information.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account.

    This will also delete all associated analysis history due to cascade delete.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content (204)
    """
    try:
        db.delete(current_user)
        db.commit()
    except Exception as e:
        logger.error(f"Delete account error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account. Please try again."
        )

    return None


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verify_data: EmailVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token (POST method with JSON body).

    Args:
        verify_data: Verification token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    user = db.query(User).filter(
        User.verification_token == verify_data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    if user.verification_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None

    try:
        db.commit()
        return {"message": "Email verified successfully. You can now log in."}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed. Please try again."
        )


@router.get("/verify", response_class=HTMLResponse)
async def verify_email_get(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token (GET method with query parameter).
    This endpoint is used for email verification links.

    Args:
        token: Verification token from query parameter
        db: Database session

    Returns:
        HTML page confirming verification
    """
    user = db.query(User).filter(
        User.verification_token == token
    ).first()

    if not user:
        return HTMLResponse(content="""
        <html>
            <body style="font-family: 'Segoe UI', sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4;">
                <div style="background-color: white; padding: 40px; border-radius: 8px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #d32f2f;">Invalid Verification Token</h2>
                    <p style="color: #555;">The token provided is invalid or has already been used.</p>
                </div>
            </body>
        </html>
        """, status_code=400)

    if user.verification_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return HTMLResponse(content="""
        <html>
            <body style="font-family: 'Segoe UI', sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4;">
                <div style="background-color: white; padding: 40px; border-radius: 8px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #d32f2f;">Token Expired</h2>
                    <p style="color: #555;">This verification link has expired. Please request a new one.</p>
                </div>
            </body>
        </html>
        """, status_code=400)

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None

    try:
        db.commit()
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        login_url = f"{frontend_url}/auth"

        # Redirect to login page after 3 seconds with success message
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="3;url={login_url}">
            <title>Email Verified</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify_content: center;
                    align_items: center;
                    height: 100vh;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }}
                h1 {{
                    color: #1a237e;
                    margin-bottom: 20px;
                }}
                p {{
                    color: #555555;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .btn {{
                    background-color: #283593;
                    color: #ffffff;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: 600;
                    display: inline-block;
                    transition: background-color 0.3s;
                }}
                .btn:hover {{
                    background-color: #1a237e;
                }}
                .success-icon {{
                    color: #4CAF50;
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✓</div>
                <h1>Email Verified Successfully!</h1>
                <p>Thank you for verifying your email address. Your account is now active and you can access all features of NeuralCoach.</p>
                <p style="color: #888; font-size: 14px;">Redirecting to login page in 3 seconds...</p>
                <a href="{login_url}" class="btn">Go to Login Now</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception:
        db.rollback()
        return HTMLResponse(content="""
        <html>
            <body style="font-family: 'Segoe UI', sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4;">
                <div style="background-color: white; padding: 40px; border-radius: 8px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #d32f2f;">Verification Failed</h2>
                    <p style="color: #555;">An internal error occurred. Please try again later.</p>
                </div>
            </body>
        </html>
        """, status_code=500)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    user_data: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend verification email.

    Args:
        user_data: Username and password
        background_tasks: Background tasks for sending email
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or already verified
    """
    user = authenticate_user(db, user_data.username, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    verification_token = generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user.verification_token = verification_token
    user.verification_token_expires = verification_expires

    try:
        db.commit()
        
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.username,
            verification_token
        )
        
        return {"message": "Verification email sent. Please check your inbox."}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again."
        )


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.

    Args:
        reset_data: Email address
        background_tasks: Background tasks for sending email
        db: Database session

    Returns:
        Success message (always returns success even if email not found for security)
    """
    user = db.query(User).filter(func.lower(User.email) == reset_data.email.lower()).first()

    if user:
        reset_token = generate_reset_token()
        reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)

        user.reset_token = reset_token
        user.reset_token_expires = reset_expires

        try:
            db.commit()
            
            background_tasks.add_task(
                send_password_reset_email,
                user.email,
                user.username,
                reset_token
            )
        except Exception:
            db.rollback()

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password with token.

    Args:
        reset_data: Reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    user = db.query(User).filter(
        User.reset_token == reset_data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    if user.reset_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None

    try:
        db.commit()
        return {"message": "Password reset successfully. You can now log in with your new password."}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user.

    Args:
        password_data: Current and new password
        background_tasks: Background tasks for sending email
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)

    try:
        db.commit()
        
        background_tasks.add_task(
            send_password_changed_email,
            current_user.email,
            current_user.username
        )
        
        return {"message": "Password changed successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )


@router.post("/upload-profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    file: UploadFile = File(..., description="Profile picture (JPG, JPEG, PNG)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload or update user profile picture.
    
    Args:
        file: Image file (JPG, JPEG, PNG, max 5MB)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user data with profile picture URL
        
    Raises:
        HTTPException: If file type invalid or upload fails
    """
    import os
    import shutil
    from pathlib import Path
    
    # Validate file type by extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided."
        )
    
    file_extension = file.filename.lower().split('.')[-1]
    allowed_extensions = ["jpg", "jpeg", "png"]
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only JPG, JPEG, and PNG allowed. Got: {file_extension}"
        )
    
    # Validate file size (max 5MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
        
    # Validate file content using magic numbers
    header = file.file.read(2048)
    file.file.seek(0)
    mime_type = magic.from_buffer(header, mime=True)
    
    allowed_mimes = ["image/jpeg", "image/png", "image/jpg"]
    if mime_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file content. Detected type: {mime_type}"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("/app/uploads/profile_pictures")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename (use already validated extension)
        filename = f"user_{current_user.id}_{datetime.now().timestamp()}.{file_extension}"
        file_path = upload_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            # Extract old file path from URL
            old_filename = current_user.profile_picture.split('/')[-1]
            old_file = upload_dir / old_filename
            if old_file.exists():
                old_file.unlink()
        
        # Update user record with URL path (not filesystem path)
        current_user.profile_picture = f"/uploads/profile_pictures/{filename}"
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        logger.error(f"Profile picture upload error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture. Please try again."
        )


@router.delete("/profile-picture", response_model=MessageResponse)
async def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user profile picture.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    from pathlib import Path
    
    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture to delete"
        )
    
    try:
        # Extract filename from URL path and delete from filesystem
        filename = current_user.profile_picture.split('/')[-1]
        upload_dir = Path("/app/uploads/profile_pictures")
        file_path = upload_dir / filename
        
        if file_path.exists():
            file_path.unlink()
        
        # Update user record
        current_user.profile_picture = None
        db.commit()
        
        return {"message": "Profile picture deleted successfully"}
        
    except Exception as e:
        logger.error(f"Profile picture delete error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile picture. Please try again."
        )
