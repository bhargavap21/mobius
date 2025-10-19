"""
Authentication middleware for FastAPI
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from auth.auth_service import AuthService
from db.models import User
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for extracting tokens from Authorization header
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)  # Optional auth - doesn't throw 401


class AuthMiddleware:
    """Middleware for handling authentication"""

    def __init__(self):
        self.auth_service = AuthService()

    async def get_current_user_id(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> UUID:
        """
        Extract and verify user ID from JWT token

        Args:
            credentials: HTTP Authorization credentials

        Returns:
            User UUID

        Raises:
            HTTPException: If token is invalid or missing
        """
        try:
            token = credentials.credentials

            user_id = await self.auth_service.verify_token(token)

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Auth middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """
        Extract and verify full user object from JWT token

        Args:
            credentials: HTTP Authorization credentials

        Returns:
            User object

        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            token = credentials.credentials

            user = await self.auth_service.get_current_user(token)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or token invalid",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Auth middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_optional_user_id(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[UUID]:
        """
        Extract user ID from token if present, return None if not

        Args:
            credentials: HTTP Authorization credentials (optional)

        Returns:
            User UUID if authenticated, None otherwise
        """
        try:
            if not credentials:
                return None

            token = credentials.credentials
            user_id = await self.auth_service.verify_token(token)

            return user_id

        except Exception as e:
            logger.warning(f"⚠️  Optional auth failed: {e}")
            return None


# Create singleton instance
auth_middleware = AuthMiddleware()


# Dependency functions for FastAPI routes
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Dependency to get current user ID"""
    return await auth_middleware.get_current_user_id(credentials)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency to get current user"""
    return await auth_middleware.get_current_user(credentials)


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[UUID]:
    """Dependency to get optional user ID (doesn't require auth)"""
    return await auth_middleware.get_optional_user_id(credentials)
