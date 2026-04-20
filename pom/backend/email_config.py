"""
Email configuration and utilities for NeuralCoach.
Updated to use localhost for MailHog.
"""
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List

mail_username = os.getenv("MAIL_USERNAME", "")
mail_password = os.getenv("MAIL_PASSWORD", "")
mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")

validate_certs = os.getenv("MAIL_VALIDATE_CERTS", "True").lower() == "true"
if "mailhog" in mail_server.lower() or "localhost" in mail_server.lower():
    validate_certs = False

conf = ConnectionConfig(
    MAIL_USERNAME=mail_username,
    MAIL_PASSWORD=mail_password,
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@neuralcoach.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=mail_server,
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=bool(mail_username and mail_password),
    VALIDATE_CERTS=validate_certs,
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "NeuralCoach")
)

fm = FastMail(conf)


async def send_verification_email(email: EmailStr, username: str, token: str):
    """
    Send account verification email.
    
    Args:
        email: Recipient email address
        username: User's username
        token: Verification token
    """
    # Use BACKEND_URL for API endpoints, fall back to localhost:8002
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8002')
    verification_url = f"{backend_url}/api/users/verify?token={token}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Account</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; color: #333333;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #1a237e; padding: 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px;">NeuralCoach</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #1a237e; margin-top: 0; font-size: 20px;">Welcome to NeuralCoach, {username}!</h2>
                                <p style="font-size: 16px; line-height: 1.6; color: #555555; margin-bottom: 25px;">
                                    Thank you for joining us. To get started with your AI-powered exercise analysis, please verify your email address by clicking the button below.
                                </p>
                                
                                <div style="text-align: center; margin: 35px 0;">
                                    <a href="{verification_url}" style="background-color: #283593; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 16px; display: inline-block; transition: background-color 0.3s;">
                                        Verify My Account
                                    </a>
                                </div>
                                
                                <p style="font-size: 14px; line-height: 1.6; color: #666666; margin-bottom: 10px;">
                                    If the button above doesn't work, you can copy and paste the following link into your browser:
                                </p>
                                <p style="font-size: 13px; line-height: 1.4; color: #1a237e; word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                                    {verification_url}
                                </p>
                                
                                <p style="font-size: 14px; line-height: 1.6; color: #888888; margin-top: 30px;">
                                    This link will expire in 24 hours for security reasons.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #eeeeee;">
                                <p style="font-size: 12px; color: #999999; margin: 0;">
                                    &copy; 2025 NeuralCoach. All rights reserved.<br>
                                    If you didn't create an account, you can safely ignore this email.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Verify Your NeuralCoach Account",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)


async def send_password_reset_email(email: EmailStr, username: str, token: str):
    """
    Send password reset email.
    
    Args:
        email: Recipient email address
        username: User's username
        token: Password reset token
    """
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2196F3;">Password Reset Request</h2>
                <p>Hi {username},</p>
                <p>We received a request to reset your password for your NeuralCoach account.</p>
                <div style="margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #666; word-break: break-all;">{reset_url}</p>
                <p>This password reset link will expire in 1 hour.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">
                    If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                </p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Reset Your NeuralCoach Password",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)


async def send_password_changed_email(email: EmailStr, username: str):
    """
    Send password changed notification email.
    
    Args:
        email: Recipient email address
        username: User's username
    """
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Password Changed Successfully</h2>
                <p>Hi {username},</p>
                <p>Your NeuralCoach account password has been changed successfully.</p>
                <p>If you made this change, you can safely ignore this email.</p>
                <p>If you didn't change your password, please contact our support team immediately and secure your account.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">
                    This is an automated notification from NeuralCoach.
                </p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Your NeuralCoach Password Was Changed",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)
