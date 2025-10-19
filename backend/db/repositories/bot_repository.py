"""
Trading bot repository for database operations
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from ..models import (
    TradingBot,
    TradingBotCreate,
    TradingBotUpdate,
    TradingBotListItem,
    PaginatedResponse
)
from ..supabase_client import get_supabase, get_supabase_admin
import logging

logger = logging.getLogger(__name__)


class BotRepository:
    """Repository for trading bot database operations"""

    def __init__(self, supabase_client: Optional[Client] = None, admin_client: Optional[Client] = None):
        """
        Initialize bot repository

        Args:
            supabase_client: Optional Supabase client instance. If not provided, uses default client.
            admin_client: Optional Supabase admin client for bypassing RLS.
        """
        self.client = supabase_client or get_supabase()
        self.admin_client = admin_client or get_supabase_admin()

    async def create(self, user_id: UUID, bot_data: TradingBotCreate) -> TradingBot:
        """
        Create a new trading bot

        Args:
            user_id: Owner's user UUID
            bot_data: Bot creation data

        Returns:
            Created TradingBot object
        """
        try:
            logger.info(f"💾 BotRepository.create() called")
            logger.info(f"💾 user_id: {user_id} (type: {type(user_id)})")
            logger.info(f"💾 bot_data.name: {bot_data.name}")
            logger.info(f"💾 bot_data.session_id: {bot_data.session_id}")

            bot_dict = {
                'user_id': str(user_id),
                'name': bot_data.name,
                'description': bot_data.description,
                'strategy_config': bot_data.strategy_config,
                'generated_code': bot_data.generated_code,
                'backtest_results': bot_data.backtest_results,
                'insights_config': bot_data.insights_config,
                'session_id': bot_data.session_id,
            }

            logger.info(f"💾 Prepared bot_dict with user_id: {bot_dict['user_id']}")
            logger.info(f"💾 Using admin_client to insert into trading_bots table...")

            # Use admin client to bypass RLS (for development/expired tokens)
            response = self.admin_client.table('trading_bots').insert(bot_dict).execute()

            logger.info(f"💾 Database response received")
            logger.info(f"💾 response.data: {response.data}")
            logger.info(f"💾 response.data length: {len(response.data) if response.data else 0}")

            if response.data and len(response.data) > 0:
                created_bot = TradingBot(**response.data[0])
                logger.info(f"✅ Bot created in database with ID: {created_bot.id}")
                return created_bot
            else:
                logger.error(f"❌ Database returned empty response!")
                raise Exception("Failed to create trading bot - empty response from database")
        except Exception as e:
            logger.error(f"❌ BotRepository.create() failed!")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ Exception message: {str(e)}")
            logger.error(f"❌ Full traceback:", exc_info=True)
            raise

    async def get_by_id(self, bot_id: UUID, user_id: UUID) -> Optional[TradingBot]:
        """
        Get trading bot by ID

        Args:
            bot_id: Bot UUID
            user_id: User UUID (for authorization)

        Returns:
            TradingBot object if found and owned by user, None otherwise
        """
        try:
            response = (
                self.client.table('trading_bots')
                .select('*')
                .eq('id', str(bot_id))
                .eq('user_id', str(user_id))
                .execute()
            )

            if response.data and len(response.data) > 0:
                return TradingBot(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting bot {bot_id}: {e}")
            raise

    async def get_by_session_id(self, session_id: str, user_id: UUID) -> Optional[TradingBot]:
        """
        Get trading bot by session ID

        Args:
            session_id: Session ID from bot generation
            user_id: User UUID (for authorization)

        Returns:
            TradingBot object if found and owned by user, None otherwise
        """
        try:
            response = (
                self.client.table('trading_bots')
                .select('*')
                .eq('session_id', session_id)
                .eq('user_id', str(user_id))
                .execute()
            )

            if response.data and len(response.data) > 0:
                return TradingBot(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting bot by session {session_id}: {e}")
            raise

    async def list_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        favorites_only: bool = False
    ) -> PaginatedResponse:
        """
        List all bots for a user with pagination

        Args:
            user_id: User UUID
            page: Page number (1-indexed)
            page_size: Number of items per page
            favorites_only: If True, only return favorite bots

        Returns:
            PaginatedResponse with TradingBotListItem objects
        """
        try:
            offset = (page - 1) * page_size

            # Build query
            query = self.client.table('trading_bots').select('*').eq('user_id', str(user_id))

            if favorites_only:
                query = query.eq('is_favorite', True)

            # Get total count
            count_response = query.execute()
            total = len(count_response.data) if count_response.data else 0

            # Get paginated data
            response = (
                query.order('created_at', desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            # Convert to list items with summary
            list_items = []
            for bot_data in response.data:
                # Extract summary from backtest results
                backtest = bot_data.get('backtest_results', {})
                list_item = TradingBotListItem(
                    id=bot_data['id'],
                    name=bot_data['name'],
                    description=bot_data.get('description'),
                    is_favorite=bot_data.get('is_favorite', False),
                    created_at=bot_data['created_at'],
                    updated_at=bot_data['updated_at'],
                    total_trades=backtest.get('total_trades'),
                    total_return=backtest.get('total_return'),
                    win_rate=backtest.get('win_rate')
                )
                list_items.append(list_item)

            return PaginatedResponse(
                data=list_items,
                total=total,
                page=page,
                page_size=page_size,
                has_more=(offset + page_size) < total
            )
        except Exception as e:
            logger.error(f"Error listing bots for user {user_id}: {e}")
            raise

    async def update(self, bot_id: UUID, user_id: UUID, update_data: TradingBotUpdate) -> TradingBot:
        """
        Update a trading bot

        Args:
            bot_id: Bot UUID
            user_id: User UUID (for authorization)
            update_data: Update data

        Returns:
            Updated TradingBot object
        """
        try:
            # Build update dict from provided fields
            update_dict = {}
            if update_data.name is not None:
                update_dict['name'] = update_data.name
            if update_data.description is not None:
                update_dict['description'] = update_data.description
            if update_data.is_favorite is not None:
                update_dict['is_favorite'] = update_data.is_favorite
            if update_data.strategy_config is not None:
                update_dict['strategy_config'] = update_data.strategy_config
            if update_data.generated_code is not None:
                update_dict['generated_code'] = update_data.generated_code
            if update_data.backtest_results is not None:
                update_dict['backtest_results'] = update_data.backtest_results
            if update_data.insights_config is not None:
                update_dict['insights_config'] = update_data.insights_config

            if not update_dict:
                # Nothing to update, just return current bot
                return await self.get_by_id(bot_id, user_id)

            response = (
                self.client.table('trading_bots')
                .update(update_dict)
                .eq('id', str(bot_id))
                .eq('user_id', str(user_id))
                .execute()
            )

            # Supabase update returns empty data due to RLS, so fetch the updated bot
            return await self.get_by_id(bot_id, user_id)
        except Exception as e:
            logger.error(f"Error updating bot {bot_id}: {e}")
            raise

    async def delete(self, bot_id: UUID, user_id: UUID) -> bool:
        """
        Delete a trading bot

        Args:
            bot_id: Bot UUID
            user_id: User UUID (for authorization)

        Returns:
            True if deleted successfully
        """
        try:
            response = (
                self.client.table('trading_bots')
                .delete()
                .eq('id', str(bot_id))
                .eq('user_id', str(user_id))
                .execute()
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting bot {bot_id}: {e}")
            raise

    async def toggle_favorite(self, bot_id: UUID, user_id: UUID) -> TradingBot:
        """
        Toggle favorite status of a bot

        Args:
            bot_id: Bot UUID
            user_id: User UUID (for authorization)

        Returns:
            Updated TradingBot object
        """
        try:
            # Get current bot
            bot = await self.get_by_id(bot_id, user_id)
            if not bot:
                raise Exception("Bot not found or unauthorized")

            # Toggle favorite
            new_favorite_status = not bot.is_favorite

            response = (
                self.client.table('trading_bots')
                .update({'is_favorite': new_favorite_status})
                .eq('id', str(bot_id))
                .eq('user_id', str(user_id))
                .execute()
            )

            if response.data and len(response.data) > 0:
                return TradingBot(**response.data[0])
            else:
                raise Exception("Failed to toggle favorite")
        except Exception as e:
            logger.error(f"Error toggling favorite for bot {bot_id}: {e}")
            raise

    async def get_favorites(self, user_id: UUID) -> List[TradingBotListItem]:
        """
        Get all favorite bots for a user

        Args:
            user_id: User UUID

        Returns:
            List of favorite TradingBotListItem objects
        """
        try:
            response = await self.list_by_user(
                user_id=user_id,
                page=1,
                page_size=1000,  # Get all favorites
                favorites_only=True
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting favorites for user {user_id}: {e}")
            raise
