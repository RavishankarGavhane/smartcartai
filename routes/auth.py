from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
import secrets
import logging
from models import User
from database import get_db
from crud import UserCRUD, SessionCRUD
from auth_utils import verify_password, create_access_token, get_password_hash
from auth import get_current_user_from_cookie
from utils.email_utils import email_service  

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

reset_tokens = {}  

# Token expiry time (hours)
TOKEN_EXPIRY_HOURS = 1


@router.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    """User registration - stores in PostgreSQL and sends welcome email"""
    try:
        form = await request.form()

        required = ["firstName", "lastName", "email", "phone", "password", "confirm_password"]
        for field in required:
            if field not in form or not form[field]:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": f"{field} is required"}
                )

        email = form["email"].strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Invalid email format"}
            )

        phone = form["phone"].strip()
        if not re.match(r"^\d{10}$", phone):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Phone must be 10 digits"}
            )

        password = form["password"]
        if len(password) < 6:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Password must be at least 6 characters"}
            )

        if password != form["confirm_password"]:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Passwords do not match"}
            )

        if UserCRUD.get_by_email(db, email):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Email already registered"}
            )

        if UserCRUD.get_by_phone(db, phone):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Phone number already registered"}
            )

        # Create user in database
        user = UserCRUD.create(
            db=db,
            first_name=form["firstName"].strip(),
            last_name=form["lastName"].strip(),
            email=email,
            phone=phone,
            password=password
        )

        try:
            email_service.send_welcome_email(user.email, user.first_name)
            logger.info(f"Welcome email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")

        # Create access token
        token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=timedelta(days=7)
        )

        # Store session
        SessionCRUD.create(
            db=db,
            user_id=user.id,
            token=token,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None
        )

        # Set cookie and redirect
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax",
            path="/"
        )
        return response

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Registration failed: {str(e)}"}
        )


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """User login"""
    try:
        form = await request.form()

        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        remember_me = form.get("remember_me") == "on"

        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Email and password required"}
            )

        user = UserCRUD.get_by_email(db, email)

        if not user or not verify_password(password, user.password_hash):
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Invalid email or password"}
            )

        if not user.is_active:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "Account is deactivated"}
            )

        UserCRUD.update_last_login(db, user.id)

        expires_delta = timedelta(days=30) if remember_me else timedelta(days=7)
        token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=expires_delta
        )

        SessionCRUD.create(
            db=db,
            user_id=user.id,
            token=token,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None
        )

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=int(expires_delta.total_seconds()),
            secure=False,
            samesite="lax",
            path="/"
        )
        return response

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Login failed: {str(e)}"}
        )


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """User logout"""
    token = request.cookies.get("access_token")
    if token:
        SessionCRUD.deactivate(db, token)

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me")
async def me(request: Request, db: Session = Depends(get_db)):
    """Get current user info"""
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Not authenticated"}
        )

    addresses = []
    for addr in user.addresses:
        addresses.append({
            "id": addr.id,
            "type": addr.type,
            "recipient_name": addr.recipient_name,
            "phone": addr.phone,
            "address_line1": addr.address_line1,
            "address_line2": addr.address_line2 or "",
            "city": addr.city,
            "state": addr.state,
            "zip": addr.zip_code,
            "isDefault": addr.is_default
        })

    return {
        "success": True,
        "user": {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "addresses": addresses
        }
    }



def cleanup_expired_tokens():
    """Remove expired tokens from memory"""
    now = datetime.now()
    expired = [token for token, data in reset_tokens.items() if now > data["expiry"]]
    for token in expired:
        del reset_tokens[token]
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired reset tokens")


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Render forgot password page"""
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot-password")
async def forgot_password(request: Request, db: Session = Depends(get_db)):
    """Handle forgot password request"""
    try:
        # Clean up expired tokens first
        cleanup_expired_tokens()
        
        form = await request.form()
        email = form.get("email", "").strip().lower()

        if not email:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Email is required"}
            )

        # Check if user exists
        user = UserCRUD.get_by_email(db, email)
        
        # Always return success even if email doesn't exist (security best practice)
        if user:
            # Generate a secure random token
            reset_token = secrets.token_urlsafe(32)
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            
            # Store token with additional info
            reset_tokens[reset_token] = {
                "user_id": user.id,
                "email": user.email,
                "expiry": expiry,
                "used": False,
                "created_at": datetime.now()
            }
            
            logger.info(f"Password reset token generated for {user.email}: {reset_token[:10]}...")
            
            # Send password reset email
            try:
                email_service.send_password_reset(user.email, user.first_name, reset_token)
                logger.info(f"Password reset email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
                # Remove token if email fails
                del reset_tokens[reset_token]
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": "Failed to send reset email. Please try again."}
                )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "If your email is registered, you will receive a password reset link shortly."
            }
        )

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An error occurred. Please try again."}
        )

        
@router.post("/reset-password-direct")
async def reset_password_direct(request: Request, db: Session = Depends(get_db)):
    """Direct password reset without email link"""
    try:
        form = await request.form()
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        confirm_password = form.get("confirm_password", "")

        # Validate inputs
        if not email or not password or not confirm_password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "All fields are required"}
            )

        if password != confirm_password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Passwords do not match"}
            )

        if len(password) < 6:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Password must be at least 6 characters"}
            )

        # Find user by email
        user = UserCRUD.get_by_email(db, email)
        if not user:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "User not found with this email"}
            )

        # Update password
        user.password_hash = get_password_hash(password)
        db.commit()
        
        logger.info(f"Password reset successful for user: {user.email}")

        try:
            email_service.send_password_reset_confirmation(user.email, user.first_name)
            logger.info(f"Password reset confirmation email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send reset confirmation: {str(e)}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Password reset successfully! You can now login with your new password."
            }
        )

    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An error occurred. Please try again."}
        )
    

@router.get("/reset-password-confirmation", response_class=HTMLResponse)
async def reset_password_confirmation_page(request: Request):
    """Render password reset confirmation page"""
    return templates.TemplateResponse("reset_password_confirmation.html", {"request": request})

