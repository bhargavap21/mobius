"""
User repository for database operations
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from supabase import Client
from ..models import User, UserCreate, UserResponse
from ..supabase_client import get_supabase, get_supabase_admin
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations"""

    def __init__(self, supabase_client: Optional[Client] = None, admin_client: Optional[Client] = None):
        """
        Initialize user repository

        Args:
            supabase_client: Optional Supabase client instance. If not provided, uses default client.
            admin_client: Optional Supabase admin client for bypassing RLS.
        """
        self.client = supabase_client or get_supabase()
        self.admin_client = admin_client or get_supabase_admin()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        try:
            response = self.client.table('users').select('*').eq('id', str(user_id)).execute()

            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            email: User email

        Returns:
            User object if found, None otherwise
        """
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()

            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    async def create(self, user_data: UserCreate, user_id: UUID) -> User:
        """
        Create a new user profile (auth user should already exist)
        Uses admin client to bypass RLS for initial user creation

        Args:
            user_data: User creation data
            user_id: UUID from Supabase auth.users

        Returns:
            Created User object
        """
        try:
            user_dict = {
                'id': str(user_id),
                'email': user_data.email,
                'full_name': user_data.full_name,
            }

            # Use admin client to bypass RLS for user creation
            response = self.admin_client.table('users').insert(user_dict).execute()

            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            else:
                raise Exception("Failed to create user profile")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def update(self, user_id: UUID, full_name: Optional[str] = None) -> User:
        """
        Update user profile

        Args:
            user_id: User UUID
            full_name: New full name

        Returns:
            Updated User object
        """
        try:
            update_data = {}
            if full_name is not None:
                update_data['full_name'] = full_name

            if not update_data:
                # Nothing to update, just return current user
                return await self.get_by_id(user_id)

            response = (
                self.client.table('users')
                .update(update_data)
                .eq('id', str(user_id))
                .execute()
            )

            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            else:
                raise Exception("User not found")
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete(self, user_id: UUID) -> bool:
        """
        Delete user profile

        Args:
            user_id: User UUID

        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.table('users').delete().eq('id', str(user_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        List all users (admin function)

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of User objects
        """
        try:
            response = (
                self.client.table('users')
                .select('*')
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [User(**user) for user in response.data]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise

    def to_response(self, user: User) -> UserResponse:
        """
        Convert User to UserResponse (without sensitive data)

        Args:
            user: User object

        Returns:
            UserResponse object
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
