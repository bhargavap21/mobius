"""
Trading bot API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional
from db.models import (
    TradingBot,
    TradingBotCreate,
    TradingBotUpdate,
    TradingBotListItem,
    PaginatedResponse,
    MessageResponse
)
from db.repositories.bot_repository import BotRepository
from middleware.auth_middleware import get_current_user_id, get_optional_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bots", tags=["trading_bots"])
bot_repo = BotRepository()


@router.post("", response_model=TradingBot, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: TradingBotCreate,
    user_id: Optional[UUID] = Depends(get_optional_user_id)
):
    """
    Create a new trading bot

    Args:
        bot_data: Bot creation data
        user_id: Current user ID (from auth token, optional for development)

    Returns:
        Created TradingBot object

    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info("="*80)
        logger.info("🚀 BOT SAVE REQUEST RECEIVED")
        logger.info(f"📝 Bot data: name='{bot_data.name}', asset='{bot_data.asset}'")
        logger.info(f"🔐 Auth user_id from middleware: {user_id}")
        logger.info(f"🔐 user_id type: {type(user_id)}")

        if user_id is None:
            logger.error("❌ CRITICAL: user_id is None after auth middleware!")
            logger.error("This means token verification failed or no token was sent")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please sign in again."
            )

        logger.info(f"✅ Authenticated user_id: {user_id}")
        logger.info(f"📤 Calling bot_repo.create(user_id={user_id}, bot_data=...)")

        bot = await bot_repo.create(user_id, bot_data)

        logger.info(f"✅ Bot created successfully: {bot.name} (ID: {bot.id})")
        logger.info("="*80)
        return bot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Bot creation failed with exception: {type(e).__name__}")
        logger.error(f"❌ Exception message: {str(e)}")
        logger.error(f"❌ Full traceback:", exc_info=True)
        logger.info("="*80)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create bot: {str(e)}"
        )


@router.get("", response_model=PaginatedResponse)
async def list_bots(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    favorites_only: bool = Query(False, description="Show only favorite bots"),
    user_id: Optional[UUID] = Depends(get_optional_user_id)
):
    """
    List all trading bots for current user

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        favorites_only: If true, only show favorite bots
        user_id: Current user ID (from auth token, optional for development)

    Returns:
        PaginatedResponse with list of TradingBotListItem objects
    """
    try:
        # Use default user ID if not authenticated
        if user_id is None:
            user_id = UUID("00000000-0000-0000-0000-000000000001")

        result = await bot_repo.list_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
            favorites_only=favorites_only
        )
        return result
    except Exception as e:
        logger.error(f"❌ List bots failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bots: {str(e)}"
        )


@router.get("/favorites", response_model=list[TradingBotListItem])
async def get_favorites(
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get all favorite bots for current user

    Args:
        user_id: Current user ID (from auth token)

    Returns:
        List of favorite TradingBotListItem objects
    """
    try:
        favorites = await bot_repo.get_favorites(user_id)
        return favorites
    except Exception as e:
        logger.error(f"❌ Get favorites failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get favorites: {str(e)}"
        )


@router.get("/{bot_id}", response_model=TradingBot)
async def get_bot(
    bot_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get a specific trading bot by ID

    Args:
        bot_id: Bot UUID
        user_id: Current user ID (from auth token)

    Returns:
        TradingBot object

    Raises:
        HTTPException: If bot not found or unauthorized
    """
    try:
        bot = await bot_repo.get_by_id(bot_id, user_id)

        if not bot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found or unauthorized"
            )

        return bot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get bot failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bot: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=TradingBot)
async def get_bot_by_session(
    session_id: str,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get a trading bot by session ID

    Args:
        session_id: Session ID from bot generation
        user_id: Current user ID (from auth token)

    Returns:
        TradingBot object

    Raises:
        HTTPException: If bot not found or unauthorized
    """
    try:
        bot = await bot_repo.get_by_session_id(session_id, user_id)

        if not bot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found for this session"
            )

        return bot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get bot by session failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bot: {str(e)}"
        )


@router.patch("/{bot_id}", response_model=TradingBot)
async def update_bot(
    bot_id: UUID,
    update_data: TradingBotUpdate,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Update a trading bot

    Args:
        bot_id: Bot UUID
        update_data: Fields to update
        user_id: Current user ID (from auth token)

    Returns:
        Updated TradingBot object

    Raises:
        HTTPException: If update fails or unauthorized
    """
    try:
        bot = await bot_repo.update(bot_id, user_id, update_data)
        logger.info(f"✅ Bot updated: {bot.name} (ID: {bot.id})")
        return bot
    except Exception as e:
        logger.error(f"❌ Bot update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update bot: {str(e)}"
        )


@router.post("/{bot_id}/favorite", response_model=TradingBot)
async def toggle_favorite(
    bot_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Toggle favorite status of a bot

    Args:
        bot_id: Bot UUID
        user_id: Current user ID (from auth token)

    Returns:
        Updated TradingBot object

    Raises:
        HTTPException: If toggle fails or unauthorized
    """
    try:
        bot = await bot_repo.toggle_favorite(bot_id, user_id)
        logger.info(f"✅ Bot favorite toggled: {bot.name} -> {bot.is_favorite}")
        return bot
    except Exception as e:
        logger.error(f"❌ Toggle favorite failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to toggle favorite: {str(e)}"
        )


@router.delete("/{bot_id}", response_model=MessageResponse)
async def delete_bot(
    bot_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete a trading bot

    Args:
        bot_id: Bot UUID
        user_id: Current user ID (from auth token)

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails or unauthorized
    """
    try:
        await bot_repo.delete(bot_id, user_id)
        logger.info(f"✅ Bot deleted: ID {bot_id}")
        return MessageResponse(
            message="Bot deleted successfully",
            success=True
        )
    except Exception as e:
        logger.error(f"❌ Bot deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete bot: {str(e)}"
        )
