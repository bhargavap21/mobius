"""
Authentication service using Supabase Auth
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from supabase import Client
from db.supabase_client import get_supabase
from db.repositories.user_repository import UserRepository
from db.models import UserCreate, UserLogin, User, UserResponse, AuthResponse
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations"""

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize auth service

        Args:
            supabase_client: Optional Supabase client instance
        """
        self.client = supabase_client or get_supabase()
        self.user_repo = UserRepository(self.client)

    async def sign_up(self, user_data: UserCreate) -> AuthResponse:
        """
        Register a new user

        Args:
            user_data: User registration data

        Returns:
            AuthResponse with user info and access token

        Raises:
            Exception: If registration fails
        """
        try:
            # Create auth user in Supabase with metadata
            # The database trigger will automatically create the user profile
            auth_response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })

            if not auth_response.user:
                raise Exception("Failed to create auth user")

            user_id = UUID(auth_response.user.id)

            # Try to create user profile using admin client
            # If trigger already created it, we'll get a duplicate key error
            import time
            try:
                user = await self.user_repo.create(user_data, user_id)
                logger.info("✅ User profile created manually")
            except Exception as create_error:
                # If we get duplicate key error, the trigger created it - fetch it
                if 'duplicate key' in str(create_error).lower() or '23505' in str(create_error):
                    logger.info("✅ User profile created by trigger, fetching...")
                    time.sleep(0.5)
                    # Use admin client to fetch since user's token isn't active yet
                    from db.repositories.user_repository import UserRepository
                    admin_repo = UserRepository()
                    # Fetch using admin client
                    response = admin_repo.admin_client.table('users').select('*').eq('id', str(user_id)).execute()
                    if response.data and len(response.data) > 0:
                        user = User(**response.data[0])
                    else:
                        raise Exception("User profile created but not retrievable")
                else:
                    raise

            # Extract token info
            access_token = auth_response.session.access_token if auth_response.session else ""
            expires_in = auth_response.session.expires_in if auth_response.session else 3600

            # Check if email is confirmed
            email_confirmed = auth_response.user.email_confirmed_at is not None if auth_response.user else False

            message = None
            if not email_confirmed:
                message = "Please check your email to confirm your account before signing in."
                logger.info(f"📧 User registered, awaiting email confirmation: {user.email}")
            else:
                logger.info(f"✅ User registered successfully: {user.email}")

            return AuthResponse(
                user=self.user_repo.to_response(user),
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                email_confirmed=email_confirmed,
                message=message
            )

        except Exception as e:
            logger.error(f"❌ Sign up failed: {e}")
            raise Exception(f"Registration failed: {str(e)}")

    async def sign_in(self, login_data: UserLogin) -> AuthResponse:
        """
        Sign in an existing user

        Args:
            login_data: User login credentials

        Returns:
            AuthResponse with user info and access token

        Raises:
            Exception: If login fails
        """
        try:
            # Authenticate with Supabase
            auth_response = self.client.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password,
            })

            if not auth_response.user or not auth_response.session:
                raise Exception("Invalid credentials")

            user_id = UUID(auth_response.user.id)

            # Get user profile
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise Exception("User profile not found")

            logger.info(f"✅ User signed in: {user.email}")

            return AuthResponse(
                user=self.user_repo.to_response(user),
                access_token=auth_response.session.access_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in
            )

        except Exception as e:
            logger.error(f"❌ Sign in failed: {e}")
            raise Exception(f"Login failed: {str(e)}")

    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out a user

        Args:
            access_token: User's access token

        Returns:
            True if sign out successful

        Raises:
            Exception: If sign out fails
        """
        try:
            self.client.auth.sign_out()
            logger.info("✅ User signed out")
            return True
        except Exception as e:
            logger.error(f"❌ Sign out failed: {e}")
            raise Exception(f"Sign out failed: {str(e)}")

    async def get_current_user(self, access_token: str) -> Optional[User]:
        """
        Get current user from access token

        Args:
            access_token: JWT access token

        Returns:
            User object if token is valid, None otherwise
        """
        try:
            # Get user from token
            user_response = self.client.auth.get_user(access_token)

            if not user_response.user:
                return None

            user_id = UUID(user_response.user.id)

            # Get full user profile
            user = await self.user_repo.get_by_id(user_id)
            return user

        except Exception as e:
            logger.error(f"❌ Get current user failed: {e}")
            return None

    async def verify_token(self, access_token: str) -> Optional[UUID]:
        """
        Verify access token and return user ID

        Args:
            access_token: JWT access token

        Returns:
            User UUID if token is valid, None otherwise
        """
        try:
            user_response = self.client.auth.get_user(access_token)

            if not user_response.user:
                return None

            return UUID(user_response.user.id)

        except Exception as e:
            logger.error(f"❌ Token verification failed: {e}")
            return None

    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh access token

        Args:
            refresh_token: Refresh token

        Returns:
            AuthResponse with new tokens

        Raises:
            Exception: If refresh fails
        """
        try:
            auth_response = self.client.auth.refresh_session(refresh_token)

            if not auth_response.session or not auth_response.user:
                raise Exception("Failed to refresh token")

            user_id = UUID(auth_response.user.id)
            user = await self.user_repo.get_by_id(user_id)

            if not user:
                raise Exception("User not found")

            logger.info(f"✅ Token refreshed for user: {user.email}")

            return AuthResponse(
                user=self.user_repo.to_response(user),
                access_token=auth_response.session.access_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in
            )

        except Exception as e:
            logger.error(f"❌ Token refresh failed: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")

    async def reset_password_email(self, email: str) -> bool:
        """
        Send password reset email

        Args:
            email: User's email

        Returns:
            True if email sent successfully

        Raises:
            Exception: If sending fails
        """
        try:
            self.client.auth.reset_password_for_email(email)
            logger.info(f"✅ Password reset email sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Password reset email failed: {e}")
            raise Exception(f"Failed to send password reset email: {str(e)}")

    async def update_password(self, access_token: str, new_password: str) -> bool:
        """
        Update user's password

        Args:
            access_token: User's access token
            new_password: New password

        Returns:
            True if password updated successfully

        Raises:
            Exception: If update fails
        """
        try:
            # Set the session first
            self.client.auth.set_session(access_token, access_token)

            # Update password
            self.client.auth.update_user({
                "password": new_password
            })

            logger.info("✅ Password updated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Password update failed: {e}")
            raise Exception(f"Password update failed: {str(e)}")
