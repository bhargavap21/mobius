"""
Live Trading Engine - Executes deployed strategies in real-time
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Any, Optional
from uuid import UUID
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from services.alpaca_service import alpaca_service
from db.repositories.deployment_repository import DeploymentRepository
from db.repositories.bot_repository import BotRepository
from db.models import DeploymentUpdate

logger = logging.getLogger(__name__)


class LiveTradingEngine:
    """
    Manages live execution of deployed trading strategies
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('America/New_York'))
        self.active_deployments: Dict[str, Dict[str, Any]] = {}  # deployment_id -> config
        self.deployment_repo = DeploymentRepository()
        self.bot_repo = BotRepository()

    def start(self):
        """Start the trading engine scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Live Trading Engine started")

            # Add job to sync deployments from database every minute
            self.scheduler.add_job(
                self._sync_deployments,
                CronTrigger(minute='*'),
                id='sync_deployments',
                replace_existing=True
            )

    def stop(self):
        """Stop the trading engine"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("🛑 Live Trading Engine stopped")

    async def _sync_deployments(self):
        """
        Sync active deployments from database
        Runs every minute to check for new/updated/stopped deployments
        """
        try:
            # Get all running deployments from database
            # Note: This would need to query all users' deployments
            # For now, we'll just log that sync is happening
            logger.debug("🔄 Syncing deployments from database...")

            # Remove stopped deployments
            for deployment_id in list(self.active_deployments.keys()):
                deployment = await self.deployment_repo.get_deployment(UUID(deployment_id))
                if not deployment or deployment.status in ['stopped', 'error']:
                    await self.remove_deployment(deployment_id)

        except Exception as e:
            logger.error(f"❌ Error syncing deployments: {e}")

    async def add_deployment(self, deployment_id: UUID) -> bool:
        """
        Add a deployment to the trading engine

        Args:
            deployment_id: Deployment UUID

        Returns:
            True if successfully added
        """
        try:
            # Get deployment details
            deployment = await self.deployment_repo.get_deployment(deployment_id)
            if not deployment:
                logger.error(f"❌ Deployment {deployment_id} not found")
                return False

            if deployment.status != 'running':
                logger.warning(f"⚠️  Deployment {deployment_id} is not in running status")
                return False

            # Get the bot's generated code
            bot = await self.bot_repo.get_by_id(deployment.bot_id)
            if not bot:
                logger.error(f"❌ Bot {deployment.bot_id} not found")
                return False

            # Store deployment config
            self.active_deployments[str(deployment_id)] = {
                'deployment': deployment,
                'bot': bot,
                'strategy_code': bot.generated_code,
                'strategy_config': bot.strategy_config
            }

            # Schedule the strategy execution
            frequency = deployment.execution_frequency
            job_id = f"deployment_{deployment_id}"

            # Map frequency to cron expression
            cron_map = {
                '1min': CronTrigger(minute='*'),
                '5min': CronTrigger(minute='*/5'),
                '15min': CronTrigger(minute='*/15'),
                '30min': CronTrigger(minute='*/30'),
                '1hour': CronTrigger(minute='0')
            }

            trigger = cron_map.get(frequency, CronTrigger(minute='*/5'))

            # Only run during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)
            # Note: For testing, we'll allow running anytime
            self.scheduler.add_job(
                self._execute_strategy,
                trigger,
                args=[str(deployment_id)],
                id=job_id,
                replace_existing=True
            )

            logger.info(f"✅ Added deployment {deployment_id} to trading engine (frequency: {frequency})")
            return True

        except Exception as e:
            logger.error(f"❌ Error adding deployment {deployment_id}: {e}")
            return False

    async def remove_deployment(self, deployment_id: str):
        """Remove a deployment from the trading engine"""
        try:
            job_id = f"deployment_{deployment_id}"

            # Remove scheduled job
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Remove from active deployments
            if deployment_id in self.active_deployments:
                del self.active_deployments[deployment_id]

            logger.info(f"🗑️  Removed deployment {deployment_id} from trading engine")

        except Exception as e:
            logger.error(f"❌ Error removing deployment {deployment_id}: {e}")

    def _is_market_open(self) -> bool:
        """
        Check if market is currently open
        Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        """
        now = datetime.now(pytz.timezone('America/New_York'))

        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check market hours
        market_open = time(9, 30)
        market_close = time(16, 0)
        current_time = now.time()

        return market_open <= current_time <= market_close

    async def _execute_strategy(self, deployment_id: str):
        """
        Execute a single iteration of a trading strategy

        This is the core method that:
        1. Runs the strategy code
        2. Generates buy/sell signals
        3. Places orders via Alpaca
        4. Updates metrics and positions
        """
        try:
            logger.info(f"🔄 Executing strategy for deployment {deployment_id}")

            # Get deployment config
            if deployment_id not in self.active_deployments:
                logger.warning(f"⚠️  Deployment {deployment_id} not found in active deployments")
                return

            config = self.active_deployments[deployment_id]
            deployment = config['deployment']
            strategy_config = config['strategy_config']
            strategy_code = config['strategy_code']

            # Check if market is open (skip for now to allow testing)
            # if not self._is_market_open():
            #     logger.debug(f"⏰ Market is closed, skipping execution for {deployment_id}")
            #     return

            # Check daily loss limit
            if deployment.daily_loss_limit:
                # TODO: Implement daily loss tracking
                pass

            # Execute the strategy code to get signals
            signal = await self._run_strategy_code(
                strategy_code,
                strategy_config,
                deployment
            )

            if not signal:
                logger.debug(f"📊 No trading signal generated for {deployment_id}")
                await self._update_metrics(deployment_id)
                return

            # Process the signal and execute trades
            await self._process_signal(deployment_id, signal)

            # Update metrics after execution
            await self._update_metrics(deployment_id)

            # Update last execution time
            await self.deployment_repo.update_deployment(
                UUID(deployment_id),
                DeploymentUpdate(last_execution_at=datetime.utcnow())
            )

        except Exception as e:
            logger.error(f"❌ Error executing strategy for deployment {deployment_id}: {e}")

            # Mark deployment as error
            await self.deployment_repo.update_deployment_status(
                UUID(deployment_id),
                'error',
                stopped_at=datetime.utcnow()
            )

            # Remove from active deployments
            await self.remove_deployment(deployment_id)

    async def _run_strategy_code(
        self,
        strategy_code: str,
        strategy_config: Dict[str, Any],
        deployment: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Execute the generated strategy code to get buy/sell signals

        Returns:
            Signal dictionary with 'action': 'buy'/'sell'/'hold', 'symbol', 'quantity', etc.
        """
        try:
            # This is a simplified version - in production you'd want to:
            # 1. Run code in a sandbox
            # 2. Set proper timeouts
            # 3. Handle errors gracefully

            # For now, we'll return a mock signal for testing
            # In production, you'd exec() the strategy code safely

            logger.debug(f"📝 Evaluating strategy for {strategy_config.get('asset', 'UNKNOWN')}")

            # Mock signal (replace with actual code execution)
            return None  # No signal = hold

        except Exception as e:
            logger.error(f"❌ Error running strategy code: {e}")
            return None

    async def _process_signal(self, deployment_id: str, signal: Dict[str, Any]):
        """
        Process a trading signal and execute the trade

        Args:
            deployment_id: Deployment UUID
            signal: Trading signal with action, symbol, quantity, etc.
        """
        try:
            action = signal.get('action')
            symbol = signal.get('symbol')
            quantity = signal.get('quantity', 1)

            if action not in ['buy', 'sell']:
                return

            logger.info(f"📈 Processing {action.upper()} signal for {symbol} (qty: {quantity})")

            # Check position size limits
            config = self.active_deployments[deployment_id]
            deployment = config['deployment']

            if deployment.max_position_size:
                # Get current price to calculate position value
                current_price = await alpaca_service.get_latest_price(symbol)
                if current_price:
                    position_value = current_price * quantity
                    if position_value > deployment.max_position_size:
                        logger.warning(f"⚠️  Position size ${position_value} exceeds limit ${deployment.max_position_size}")
                        return

            # Place the order
            order = await alpaca_service.place_market_order(
                symbol=symbol,
                qty=quantity,
                side=action
            )

            # Log the trade
            await self.deployment_repo.log_trade(
                UUID(deployment_id),
                {
                    'alpaca_order_id': order['order_id'],
                    'alpaca_order_status': order['status'],
                    'symbol': symbol,
                    'side': action,
                    'order_type': 'market',
                    'quantity': quantity,
                    'filled_qty': order.get('filled_qty'),
                    'filled_avg_price': order.get('filled_avg_price'),
                    'total_value': order.get('filled_avg_price', 0) * quantity if order.get('filled_avg_price') else None,
                    'signal_metadata': signal
                }
            )

            logger.info(f"✅ {action.upper()} order placed: {quantity} {symbol}, Order ID: {order['order_id']}")

        except Exception as e:
            logger.error(f"❌ Error processing signal: {e}")

    async def _update_metrics(self, deployment_id: str):
        """Update deployment metrics from Alpaca account"""
        try:
            # Get current account status
            account = await alpaca_service.get_account()
            positions = await alpaca_service.get_positions()

            config = self.active_deployments[deployment_id]
            deployment = config['deployment']

            # Calculate metrics
            portfolio_value = float(account['portfolio_value'])
            cash = float(account['cash'])
            positions_value = portfolio_value - cash

            initial_capital = deployment.initial_capital
            total_return_pct = ((portfolio_value - initial_capital) / initial_capital) * 100

            # Log metrics
            await self.deployment_repo.log_metrics(
                UUID(deployment_id),
                {
                    'portfolio_value': portfolio_value,
                    'cash': cash,
                    'positions_value': positions_value,
                    'total_return_pct': total_return_pct,
                    'unrealized_pnl': sum(float(p.get('unrealized_pl', 0)) for p in positions),
                    'open_positions_count': len(positions)
                }
            )

            # Update deployment current capital
            await self.deployment_repo.update_deployment(
                UUID(deployment_id),
                DeploymentUpdate(
                    current_capital=portfolio_value,
                    total_pnl=portfolio_value - initial_capital,
                    total_return_pct=total_return_pct
                )
            )

            # Sync positions
            for pos in positions:
                await self.deployment_repo.upsert_position(
                    UUID(deployment_id),
                    {
                        'symbol': pos['symbol'],
                        'quantity': float(pos['qty']),
                        'average_entry_price': float(pos['avg_entry_price']),
                        'current_price': float(pos['current_price']),
                        'market_value': float(pos['market_value']),
                        'cost_basis': float(pos['cost_basis']),
                        'unrealized_pnl': float(pos['unrealized_pl']),
                        'unrealized_pnl_pct': float(pos['unrealized_plpc']) * 100
                    }
                )

            logger.debug(f"📊 Updated metrics for {deployment_id}: ${portfolio_value:,.2f} ({total_return_pct:+.2f}%)")

        except Exception as e:
            logger.error(f"❌ Error updating metrics: {e}")


# Global trading engine instance
trading_engine = LiveTradingEngine()
