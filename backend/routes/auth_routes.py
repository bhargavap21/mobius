"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from db.models import UserCreate, UserLogin, AuthResponse, MessageResponse, UserResponse, User
from auth.auth_service import AuthService
from middleware.auth_middleware import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate):
    """
    Register a new user

    Args:
        user_data: User registration data (email, password, full_name)

    Returns:
        AuthResponse with user info and access token

    Raises:
        HTTPException: If registration fails
    """
    try:
        auth_response = await auth_service.sign_up(user_data)
        return auth_response
    except Exception as e:
        logger.error(f"❌ Signup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(login_data: UserLogin):
    """
    Sign in an existing user

    Args:
        login_data: User credentials (email, password)

    Returns:
        AuthResponse with user info and access token

    Raises:
        HTTPException: If login fails
    """
    try:
        auth_response = await auth_service.sign_in(login_data)
        return auth_response
    except Exception as e:
        logger.error(f"❌ Signin failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/signout", response_model=MessageResponse)
async def sign_out(current_user: User = Depends(get_current_user)):
    """
    Sign out current user

    Args:
        current_user: Current authenticated user (from token)

    Returns:
        Success message

    Raises:
        HTTPException: If sign out fails
    """
    try:
        # Note: Supabase handles session invalidation on client side
        # Server-side we just verify the user is authenticated
        logger.info(f"✅ User {current_user.email} signed out")
        return MessageResponse(
            message="Signed out successfully",
            success=True
        )
    except Exception as e:
        logger.error(f"❌ Signout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile

    Args:
        current_user: Current authenticated user (from token)

    Returns:
        UserResponse with user profile data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(email: str):
    """
    Request password reset email

    Args:
        email: User's email address

    Returns:
        Success message

    Raises:
        HTTPException: If request fails
    """
    try:
        await auth_service.reset_password_email(email)
        return MessageResponse(
            message="Password reset email sent",
            success=True
        )
    except Exception as e:
        logger.error(f"❌ Password reset request failed: {e}")
        # Don't reveal if email exists or not
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token

    Args:
        refresh_token: Refresh token from previous authentication

    Returns:
        AuthResponse with new access token

    Raises:
        HTTPException: If refresh fails
    """
    try:
        auth_response = await auth_service.refresh_token(refresh_token)
        return auth_response
    except Exception as e:
        logger.error(f"❌ Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
