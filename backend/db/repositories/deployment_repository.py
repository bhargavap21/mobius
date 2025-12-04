"""
Deployment repository for database operations
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from ..models import (
    Deployment,
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentTrade,
    DeploymentMetrics,
    DeploymentPosition
)
from ..supabase_client import get_supabase, get_supabase_admin
import logging
import json

logger = logging.getLogger(__name__)


class DeploymentRepository:
    """Repository for deployment database operations"""

    def __init__(self, supabase_client: Optional[Client] = None, admin_client: Optional[Client] = None):
        """
        Initialize deployment repository

        Args:
            supabase_client: Optional Supabase client instance
            admin_client: Optional Supabase admin client for bypassing RLS
        """
        self.client = supabase_client or get_supabase()
        self.admin_client = admin_client or get_supabase_admin()

    async def create_deployment(
        self,
        user_id: UUID,
        deployment_data: DeploymentCreate,
        alpaca_account_id: Optional[str] = None
    ) -> Deployment:
        """
        Create a new deployment

        Args:
            user_id: User UUID
            deployment_data: Deployment creation data
            alpaca_account_id: Alpaca account identifier

        Returns:
            Created Deployment object
        """
        try:
            deployment_dict = {
                'user_id': str(user_id),
                'bot_id': str(deployment_data.bot_id),
                'status': 'running',
                'alpaca_account_id': alpaca_account_id,
                'initial_capital': deployment_data.initial_capital,
                'current_capital': deployment_data.initial_capital,
                'total_pnl': 0.0,
                'total_return_pct': 0.0,
                'execution_frequency': deployment_data.execution_frequency,
                'max_position_size': deployment_data.max_position_size,
                'daily_loss_limit': deployment_data.daily_loss_limit,
                'metadata': {}
            }

            logger.info(f"📤 Creating deployment for bot_id: {str(deployment_data.bot_id)}")
            logger.info(f"📋 Deployment dict types: {[(k, type(v).__name__) for k, v in deployment_dict.items()]}")

            # Test JSON serialization
            try:
                json.dumps(deployment_dict)
                logger.info("✅ Dict is JSON serializable")
            except Exception as json_err:
                logger.error(f"❌ Dict is NOT JSON serializable: {json_err}")
                raise

            response = self.admin_client.table('deployments').insert(deployment_dict).execute()

            if response.data and len(response.data) > 0:
                deployment = Deployment(**response.data[0])
                logger.info(f"✅ Deployment created with ID: {deployment.id}")
                return deployment
            else:
                raise Exception("Failed to create deployment - empty response")

        except Exception as e:
            logger.error(f"❌ Error creating deployment: {e}")
            raise

    async def get_deployment(self, deployment_id: UUID) -> Optional[Deployment]:
        """
        Get deployment by ID

        Args:
            deployment_id: Deployment UUID

        Returns:
            Deployment object or None
        """
        try:
            response = self.admin_client.table('deployments')\
                .select('*')\
                .eq('id', str(deployment_id))\
                .execute()

            if response.data and len(response.data) > 0:
                return Deployment(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error fetching deployment {deployment_id}: {e}")
            return None

    async def get_user_deployments(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Deployment]:
        """
        Get all deployments for a user

        Args:
            user_id: User UUID
            status: Optional status filter (running, paused, stopped, error)
            limit: Maximum number of results

        Returns:
            List of Deployment objects
        """
        try:
            query = self.admin_client.table('deployments')\
                .select('*')\
                .eq('user_id', str(user_id))\
                .order('deployed_at', desc=True)\
                .limit(limit)

            if status:
                query = query.eq('status', status)

            response = query.execute()

            if response.data:
                return [Deployment(**item) for item in response.data]
            return []

        except Exception as e:
            logger.error(f"❌ Error fetching user deployments: {e}")
            return []

    async def get_all_running_deployments(self, limit: int = 1000) -> List[Deployment]:
        """
        Get all running deployments across all users
        Used by trading engine to sync active deployments

        Args:
            limit: Maximum number of results

        Returns:
            List of Deployment objects with status 'running'
        """
        try:
            response = self.admin_client.table('deployments')\
                .select('*')\
                .eq('status', 'running')\
                .order('deployed_at', desc=True)\
                .limit(limit)\
                .execute()

            if response.data:
                return [Deployment(**item) for item in response.data]
            return []

        except Exception as e:
            logger.error(f"❌ Error fetching all running deployments: {e}")
            return []

    async def update_deployment(
        self,
        deployment_id: UUID,
        update_data: DeploymentUpdate
    ) -> Optional[Deployment]:
        """
        Update deployment

        Args:
            deployment_id: Deployment UUID
            update_data: Update data

        Returns:
            Updated Deployment object or None
        """
        try:
            # Build update dict from non-None values
            update_dict = {
                k: v for k, v in update_data.model_dump().items()
                if v is not None
            }

            if not update_dict:
                logger.warning("No fields to update")
                return await self.get_deployment(deployment_id)

            logger.info(f"📝 Updating deployment {deployment_id}: {update_dict}")

            response = self.admin_client.table('deployments')\
                .update(update_dict)\
                .eq('id', str(deployment_id))\
                .execute()

            if response.data and len(response.data) > 0:
                return Deployment(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error updating deployment: {e}")
            raise

    async def update_deployment_status(
        self,
        deployment_id: UUID,
        status: str,
        stopped_at: Optional[datetime] = None
    ) -> bool:
        """
        Update deployment status

        Args:
            deployment_id: Deployment UUID
            status: New status (running, paused, stopped, error)
            stopped_at: Optional timestamp for stopped/error status

        Returns:
            True if successful
        """
        try:
            update_dict = {'status': status}
            if stopped_at:
                update_dict['stopped_at'] = stopped_at.isoformat()

            response = self.admin_client.table('deployments')\
                .update(update_dict)\
                .eq('id', str(deployment_id))\
                .execute()

            logger.info(f"✅ Deployment {deployment_id} status updated to: {status}")
            return bool(response.data)

        except Exception as e:
            logger.error(f"❌ Error updating deployment status: {e}")
            return False

    async def log_trade(
        self,
        deployment_id: UUID,
        trade_data: Dict[str, Any]
    ) -> Optional[DeploymentTrade]:
        """
        Log a trade execution

        Args:
            deployment_id: Deployment UUID
            trade_data: Trade details

        Returns:
            Created DeploymentTrade object or None
        """
        try:
            trade_dict = {
                'deployment_id': str(deployment_id),
                **trade_data
            }

            logger.info(f"💰 Logging trade for deployment {deployment_id}: {trade_data.get('symbol')} {trade_data.get('side')}")

            response = self.admin_client.table('deployment_trades')\
                .insert(trade_dict)\
                .execute()

            if response.data and len(response.data) > 0:
                return DeploymentTrade(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error logging trade: {e}")
            return None

    async def get_deployment_trades(
        self,
        deployment_id: UUID,
        limit: int = 100
    ) -> List[DeploymentTrade]:
        """
        Get trade history for a deployment

        Args:
            deployment_id: Deployment UUID
            limit: Maximum number of trades

        Returns:
            List of DeploymentTrade objects
        """
        try:
            response = self.admin_client.table('deployment_trades')\
                .select('*')\
                .eq('deployment_id', str(deployment_id))\
                .order('submitted_at', desc=True)\
                .limit(limit)\
                .execute()

            if response.data:
                return [DeploymentTrade(**item) for item in response.data]
            return []

        except Exception as e:
            logger.error(f"❌ Error fetching trades: {e}")
            return []

    async def log_metrics(
        self,
        deployment_id: UUID,
        metrics_data: Dict[str, Any]
    ) -> Optional[DeploymentMetrics]:
        """
        Log performance metrics snapshot

        Args:
            deployment_id: Deployment UUID
            metrics_data: Metrics data

        Returns:
            Created DeploymentMetrics object or None
        """
        try:
            metrics_dict = {
                'deployment_id': str(deployment_id),
                **metrics_data
            }

            response = self.admin_client.table('deployment_metrics')\
                .insert(metrics_dict)\
                .execute()

            if response.data and len(response.data) > 0:
                return DeploymentMetrics(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error logging metrics: {e}")
            return None

    async def get_deployment_metrics(
        self,
        deployment_id: UUID,
        limit: int = 1000
    ) -> List[DeploymentMetrics]:
        """
        Get metrics history for a deployment

        Args:
            deployment_id: Deployment UUID
            limit: Maximum number of metrics snapshots

        Returns:
            List of DeploymentMetrics objects
        """
        try:
            response = self.admin_client.table('deployment_metrics')\
                .select('*')\
                .eq('deployment_id', str(deployment_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()

            if response.data:
                return [DeploymentMetrics(**item) for item in response.data]
            return []

        except Exception as e:
            logger.error(f"❌ Error fetching metrics: {e}")
            return []

    async def upsert_position(
        self,
        deployment_id: UUID,
        position_data: Dict[str, Any]
    ) -> Optional[DeploymentPosition]:
        """
        Create or update a position

        Args:
            deployment_id: Deployment UUID
            position_data: Position data

        Returns:
            DeploymentPosition object or None
        """
        try:
            position_dict = {
                'deployment_id': str(deployment_id),
                **position_data
            }

            response = self.admin_client.table('deployment_positions')\
                .upsert(position_dict, on_conflict='deployment_id,symbol')\
                .execute()

            if response.data and len(response.data) > 0:
                return DeploymentPosition(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error upserting position: {e}")
            return None

    async def get_deployment_positions(
        self,
        deployment_id: UUID
    ) -> List[DeploymentPosition]:
        """
        Get all open positions for a deployment

        Args:
            deployment_id: Deployment UUID

        Returns:
            List of DeploymentPosition objects
        """
        try:
            response = self.admin_client.table('deployment_positions')\
                .select('*')\
                .eq('deployment_id', str(deployment_id))\
                .execute()

            if response.data:
                return [DeploymentPosition(**item) for item in response.data]
            return []

        except Exception as e:
            logger.error(f"❌ Error fetching positions: {e}")
            return []

    async def delete_position(
        self,
        deployment_id: UUID,
        symbol: str
    ) -> bool:
        """
        Delete a position (when fully closed)

        Args:
            deployment_id: Deployment UUID
            symbol: Stock symbol

        Returns:
            True if successful
        """
        try:
            response = self.admin_client.table('deployment_positions')\
                .delete()\
                .eq('deployment_id', str(deployment_id))\
                .eq('symbol', symbol)\
                .execute()

            logger.info(f"✅ Deleted position {symbol} from deployment {deployment_id}")
            return bool(response.data)

        except Exception as e:
            logger.error(f"❌ Error deleting position: {e}")
            return False
