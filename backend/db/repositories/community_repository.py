"""
Community repository for shared agent database operations
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from ..models import (
    SharedAgent,
    SharedAgentCreate,
    SharedAgentUpdate,
    SharedAgentListItem,
    AgentLike,
    AgentDownload,
    PaginatedResponse
)
from ..supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)


class CommunityRepository:
    """Repository for community shared agent database operations"""

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize community repository

        Args:
            supabase_client: Optional Supabase client instance. If not provided, uses default client.
        """
        self.client = supabase_client or get_supabase()

    async def create_shared_agent(self, author_id: UUID, shared_agent_data: SharedAgentCreate) -> SharedAgent:
        """
        Create a new shared agent

        Args:
            author_id: Author's user UUID
            shared_agent_data: Shared agent creation data

        Returns:
            Created SharedAgent object
        """
        try:
            # Get the original bot data to copy strategy and backtest results
            original_bot_response = self.client.table('trading_bots').select('*').eq('id', str(shared_agent_data.original_bot_id)).eq('user_id', str(author_id)).execute()
            
            if not original_bot_response.data:
                raise Exception("Original bot not found or not owned by user")

            original_bot = original_bot_response.data[0]
            
            shared_agent_dict = {
                'original_bot_id': str(shared_agent_data.original_bot_id),
                'author_id': str(author_id),
                'name': shared_agent_data.name,
                'description': shared_agent_data.description,
                'tags': shared_agent_data.tags,
                'is_public': shared_agent_data.is_public,
            }

            response = self.client.table('shared_agents').insert(shared_agent_dict).execute()

            if response.data and len(response.data) > 0:
                return SharedAgent(**response.data[0])
            else:
                raise Exception("Failed to create shared agent")
        except Exception as e:
            logger.error(f"Error creating shared agent: {e}")
            raise

    async def get_shared_agents(self, page: int = 1, page_size: int = 20, user_id: Optional[UUID] = None) -> PaginatedResponse:
        """
        Get paginated list of shared agents

        Args:
            page: Page number
            page_size: Items per page
            user_id: Optional user ID to check if they liked each agent

        Returns:
            PaginatedResponse with shared agents
        """
        try:
            # Calculate offset
            offset = (page - 1) * page_size

            # Build query for public shared agents
            query = self.client.table('shared_agents').select('*').eq('is_public', True).order('shared_at', desc=True)
            
            # Get total count
            count_response = self.client.table('shared_agents').select('id', count='exact').eq('is_public', True).execute()
            total = count_response.count or 0

            # Get paginated results
            response = query.range(offset, offset + page_size - 1).execute()
            
            agents = []
            for agent_data in response.data:
                agent = SharedAgent(**agent_data)
                
                # Check if current user liked this agent
                if user_id:
                    like_response = self.client.table('agent_likes').select('id').eq('shared_agent_id', str(agent.id)).eq('user_id', str(user_id)).execute()
                    agent.liked = len(like_response.data) > 0
                
                agents.append(agent)

            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                items=agents,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f"Error getting shared agents: {e}")
            raise

    async def get_shared_agent_by_id(self, agent_id: UUID, user_id: Optional[UUID] = None) -> Optional[SharedAgent]:
        """
        Get a shared agent by ID

        Args:
            agent_id: Shared agent UUID
            user_id: Optional user ID to check if they liked the agent

        Returns:
            SharedAgent object or None if not found
        """
        try:
            response = self.client.table('shared_agents').select('*').eq('id', str(agent_id)).eq('is_public', True).execute()
            
            if not response.data:
                return None

            agent = SharedAgent(**response.data[0])
            
            # Check if current user liked this agent
            if user_id:
                like_response = self.client.table('agent_likes').select('id').eq('shared_agent_id', str(agent.id)).eq('user_id', str(user_id)).execute()
                agent.liked = len(like_response.data) > 0

            return agent
        except Exception as e:
            logger.error(f"Error getting shared agent: {e}")
            raise

    async def like_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """
        Like or unlike a shared agent

        Args:
            agent_id: Shared agent UUID
            user_id: User UUID

        Returns:
            True if liked, False if unliked
        """
        try:
            # Check if already liked
            existing_like = self.client.table('agent_likes').select('id').eq('shared_agent_id', str(agent_id)).eq('user_id', str(user_id)).execute()
            
            if existing_like.data:
                # Unlike - remove the like
                self.client.table('agent_likes').delete().eq('shared_agent_id', str(agent_id)).eq('user_id', str(user_id)).execute()
                
                # Decrement like count
                self.client.table('shared_agents').update({'likes': self.client.table('shared_agents').select('likes').eq('id', str(agent_id)).execute().data[0]['likes'] - 1}).eq('id', str(agent_id)).execute()
                
                return False
            else:
                # Like - add the like
                self.client.table('agent_likes').insert({
                    'shared_agent_id': str(agent_id),
                    'user_id': str(user_id)
                }).execute()
                
                # Increment like count
                self.client.table('shared_agents').update({'likes': self.client.table('shared_agents').select('likes').eq('id', str(agent_id)).execute().data[0]['likes'] + 1}).eq('id', str(agent_id)).execute()
                
                return True
        except Exception as e:
            logger.error(f"Error liking agent: {e}")
            raise

    async def download_agent(self, agent_id: UUID, user_id: Optional[UUID] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Download a shared agent (get original bot data and increment download count)

        Args:
            agent_id: Shared agent UUID
            user_id: Optional user UUID (for authenticated downloads)
            ip_address: Optional IP address (for anonymous downloads)
            user_agent: Optional user agent string

        Returns:
            Original bot data or None if not found
        """
        try:
            # Get the shared agent
            shared_agent_response = self.client.table('shared_agents').select('*').eq('id', str(agent_id)).eq('is_public', True).execute()
            
            if not shared_agent_response.data:
                return None

            shared_agent = shared_agent_response.data[0]
            
            # Get the original bot data
            original_bot_response = self.client.table('trading_bots').select('*').eq('id', str(shared_agent['original_bot_id'])).execute()
            
            if not original_bot_response.data:
                return None

            original_bot = original_bot_response.data[0]
            
            # Record the download
            download_data = {
                'shared_agent_id': str(agent_id),
                'downloaded_at': datetime.now().isoformat()
            }
            
            if user_id:
                download_data['user_id'] = str(user_id)
            if ip_address:
                download_data['ip_address'] = ip_address
            if user_agent:
                download_data['user_agent'] = user_agent

            self.client.table('agent_downloads').insert(download_data).execute()
            
            # Increment download count
            current_downloads = self.client.table('shared_agents').select('downloads').eq('id', str(agent_id)).execute().data[0]['downloads']
            self.client.table('shared_agents').update({'downloads': current_downloads + 1}).eq('id', str(agent_id)).execute()
            
            return original_bot
        except Exception as e:
            logger.error(f"Error downloading agent: {e}")
            raise

    async def increment_view(self, agent_id: UUID) -> None:
        """
        Increment view count for a shared agent

        Args:
            agent_id: Shared agent UUID
        """
        try:
            current_views = self.client.table('shared_agents').select('views').eq('id', str(agent_id)).execute().data[0]['views']
            self.client.table('shared_agents').update({'views': current_views + 1}).eq('id', str(agent_id)).execute()
        except Exception as e:
            logger.error(f"Error incrementing view count: {e}")
            # Don't raise - view count is not critical

    async def get_user_shared_agents(self, user_id: UUID, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """
        Get shared agents created by a specific user

        Args:
            user_id: User UUID
            page: Page number
            page_size: Items per page

        Returns:
            PaginatedResponse with user's shared agents
        """
        try:
            offset = (page - 1) * page_size

            # Get total count
            count_response = self.client.table('shared_agents').select('id', count='exact').eq('author_id', str(user_id)).execute()
            total = count_response.count or 0

            # Get paginated results
            response = self.client.table('shared_agents').select('*').eq('author_id', str(user_id)).order('shared_at', desc=True).range(offset, offset + page_size - 1).execute()
            
            agents = [SharedAgent(**agent_data) for agent_data in response.data]
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                items=agents,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f"Error getting user shared agents: {e}")
            raise
