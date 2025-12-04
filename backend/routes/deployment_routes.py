"""
API routes for deployment management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from db.models import (
    Deployment,
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentTrade,
    DeploymentMetrics,
    DeploymentPosition,
    MessageResponse
)
from db.repositories.deployment_repository import DeploymentRepository
from db.repositories.bot_repository import BotRepository
from services.alpaca_service import alpaca_service
from services.live_trading_engine import trading_engine
from middleware.auth_middleware import get_current_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.post("", response_model=Deployment)
async def create_deployment(
    deployment_data: DeploymentCreate,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Deploy a trading bot to Alpaca paper trading

    This endpoint:
    1. Validates the bot exists and belongs to the user
    2. Retrieves Alpaca account info
    3. Creates deployment record
    4. Returns deployment details

    NOTE: The actual strategy execution loop needs to be started separately
    """
    try:
        # Validate bot exists and user owns it
        bot_repo = BotRepository()
        bot = await bot_repo.get_by_id(deployment_data.bot_id, user_id)

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to deploy this bot")

        # Get Alpaca account info
        account_info = await alpaca_service.get_account()

        if account_info.get('trading_blocked') or account_info.get('account_blocked'):
            raise HTTPException(
                status_code=400,
                detail="Alpaca account is blocked from trading"
            )

        logger.info(f"🚀 Deploying bot {bot.name} for user {user_id}")
        logger.info(f"💰 Alpaca account balance: ${account_info.get('cash')}")

        # Create deployment record
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.create_deployment(
            user_id=user_id,
            deployment_data=deployment_data,
            alpaca_account_id=account_info.get('account_id')
        )

        # Log initial metrics
        await deployment_repo.log_metrics(
            deployment_id=deployment.id,
            metrics_data={
                'portfolio_value': deployment.initial_capital,
                'cash': deployment.initial_capital,
                'positions_value': 0.0,
                'total_return_pct': 0.0,
                'daily_pnl': 0.0,
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0,
                'open_positions_count': 0,
                'total_trades_count': 0,
                'winning_trades_count': 0,
                'losing_trades_count': 0
            }
        )

        logger.info(f"✅ Deployment created: {deployment.id}")

        # Auto-activate deployment if status is 'running'
        if deployment.status == 'running':
            try:
                success = await trading_engine.add_deployment(deployment.id)
                if success:
                    logger.info(f"✅ Auto-activated deployment {deployment.id}")
                else:
                    logger.warning(f"⚠️  Failed to auto-activate deployment {deployment.id}")
            except Exception as e:
                logger.error(f"❌ Error auto-activating deployment: {e}")

        # Convert to dict with JSON-serializable types
        return deployment.model_dump(mode='json')

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Deployment])
async def get_user_deployments(
    status: Optional[str] = None,
    limit: int = 50,
    user_id: UUID = Depends(get_current_user_id)
):
    """Get all deployments for the current user"""
    try:
        deployment_repo = DeploymentRepository()
        deployments = await deployment_repo.get_user_deployments(
            user_id=user_id,
            status=status,
            limit=limit
        )
        return deployments

    except Exception as e:
        logger.error(f"❌ Error fetching deployments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}", response_model=Deployment)
async def get_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """Get deployment details"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        return deployment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/pause", response_model=MessageResponse)
async def pause_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """Pause a running deployment"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if deployment.status != 'running':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause deployment with status: {deployment.status}"
            )

        # Update status to paused
        success = await deployment_repo.update_deployment_status(
            deployment_id=deployment_id,
            status='paused'
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to pause deployment")

        logger.info(f"⏸️  Deployment {deployment_id} paused")

        return MessageResponse(
            message="Deployment paused successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error pausing deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/resume", response_model=MessageResponse)
async def resume_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """Resume a paused deployment"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if deployment.status != 'paused':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot resume deployment with status: {deployment.status}"
            )

        # Update status to running
        success = await deployment_repo.update_deployment_status(
            deployment_id=deployment_id,
            status='running'
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to resume deployment")

        logger.info(f"▶️  Deployment {deployment_id} resumed")

        return MessageResponse(
            message="Deployment resumed successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error resuming deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/stop", response_model=MessageResponse)
async def stop_deployment(
    deployment_id: UUID,
    close_positions: bool = False,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Stop a deployment permanently

    Args:
        close_positions: If True, close all open positions before stopping
    """
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if deployment.status == 'stopped':
            raise HTTPException(status_code=400, detail="Deployment already stopped")

        # Optionally close all positions
        if close_positions:
            logger.info(f"🚫 Closing all positions for deployment {deployment_id}")
            await alpaca_service.close_all_positions()

        # Update status to stopped
        success = await deployment_repo.update_deployment_status(
            deployment_id=deployment_id,
            status='stopped',
            stopped_at=datetime.utcnow()
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop deployment")

        logger.info(f"⏹️  Deployment {deployment_id} stopped")

        return MessageResponse(
            message="Deployment stopped successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error stopping deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}/trades", response_model=List[DeploymentTrade])
async def get_deployment_trades(
    deployment_id: UUID,
    limit: int = 100,
    user_id: UUID = Depends(get_current_user_id)
):
    """Get trade history for a deployment"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        trades = await deployment_repo.get_deployment_trades(
            deployment_id=deployment_id,
            limit=limit
        )

        return trades

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}/metrics", response_model=List[DeploymentMetrics])
async def get_deployment_metrics(
    deployment_id: UUID,
    limit: int = 1000,
    user_id: UUID = Depends(get_current_user_id)
):
    """Get performance metrics history for a deployment"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        metrics = await deployment_repo.get_deployment_metrics(
            deployment_id=deployment_id,
            limit=limit
        )

        return metrics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}/positions", response_model=List[DeploymentPosition])
async def get_deployment_positions(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """Get current open positions for a deployment"""
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        positions = await deployment_repo.get_deployment_positions(
            deployment_id=deployment_id
        )

        return positions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/activate", response_model=MessageResponse)
async def activate_deployment(
    deployment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Activate a deployment and start live trading

    This endpoint:
    1. Validates the deployment exists and is in 'running' status
    2. Adds the deployment to the trading engine
    3. Starts executing the strategy at the configured frequency
    """
    try:
        deployment_repo = DeploymentRepository()
        deployment = await deployment_repo.get_deployment(deployment_id)

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        if deployment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if deployment.status != 'running':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot activate deployment with status: {deployment.status}"
            )

        # Add to trading engine
        success = await trading_engine.add_deployment(deployment_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to activate deployment")

        logger.info(f"✅ Deployment {deployment_id} activated and added to trading engine")

        return MessageResponse(
            message=f"Deployment activated successfully. Strategy will execute every {deployment.execution_frequency}.",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error activating deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
