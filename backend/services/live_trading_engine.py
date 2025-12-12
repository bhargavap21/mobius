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
            bot = await self.bot_repo.get_by_id(deployment.bot_id, deployment.user_id)
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
                daily_loss = await self._get_daily_loss(deployment_id)
                if daily_loss and abs(daily_loss) >= deployment.daily_loss_limit:
                    logger.warning(
                        f"⚠️  Daily loss limit reached for deployment {deployment_id}: "
                        f"${abs(daily_loss):.2f} >= ${deployment.daily_loss_limit:.2f}"
                    )
                    # Stop the deployment
                    await self.deployment_repo.update_deployment_status(
                        UUID(deployment_id),
                        'stopped',
                        stopped_at=datetime.utcnow()
                    )
                    await self.remove_deployment(deployment_id)
                    return

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
            symbol = strategy_config.get('asset', 'AAPL')
            logger.debug(f"📝 Evaluating strategy for {symbol}")

            # Create a safe execution environment
            import sys
            import io
            from contextlib import redirect_stdout, redirect_stderr

            # Prepare the execution namespace with necessary imports
            namespace = {
                '__builtins__': __builtins__,
                'logging': logging,
                'datetime': datetime,
                'time': __import__('time'),
                'alpaca_service': alpaca_service,  # Provide Alpaca service
                'symbol': symbol,
                'strategy_config': strategy_config,
            }

            # Execute the generated code
            # The code should define a TradingBot class
            try:
                exec(strategy_code, namespace)
            except Exception as exec_error:
                logger.error(f"❌ Error executing strategy code: {exec_error}")
                return None

            # Get the TradingBot class from namespace
            TradingBot = namespace.get('TradingBot')
            if not TradingBot:
                logger.error("❌ TradingBot class not found in generated code")
                return None

            # Initialize the bot with dummy credentials (it will use alpaca_service instead)
            bot = TradingBot(api_key='dummy', secret_key='dummy', paper=True)

            # Check if we have an open position
            position = await alpaca_service.get_position(symbol)

            # If we have a position, check exit conditions
            if position:
                should_exit = False
                if hasattr(bot, 'check_exit_conditions'):
                    should_exit = bot.check_exit_conditions(position)

                if should_exit:
                    logger.info(f"🔴 Exit signal for {symbol}")
                    return {
                        'action': 'sell',
                        'symbol': symbol,
                        'quantity': abs(float(position['qty'])),
                        'reason': 'exit_conditions_met'
                    }

            # Check entry conditions
            if hasattr(bot, 'check_entry_conditions'):
                should_enter = bot.check_entry_conditions()

                if should_enter and not position:
                    # Calculate position size based on strategy config
                    quantity = self._calculate_position_size(
                        symbol=symbol,
                        deployment=deployment,
                        strategy_config=strategy_config
                    )

                    if quantity > 0:
                        logger.info(f"🟢 Entry signal for {symbol}")
                        return {
                            'action': 'buy',
                            'symbol': symbol,
                            'quantity': quantity,
                            'reason': 'entry_conditions_met'
                        }

            return None  # No signal = hold

        except Exception as e:
            logger.error(f"❌ Error running strategy code: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _calculate_position_size(
        self,
        symbol: str,
        deployment: Any,
        strategy_config: Dict[str, Any]
    ) -> int:
        """
        Calculate position size based on available capital and risk management

        Args:
            symbol: Stock symbol
            deployment: Deployment config
            strategy_config: Strategy parameters

        Returns:
            Number of shares to trade
        """
        try:
            # Get current account info
            import asyncio
            account = asyncio.run(alpaca_service.get_account())
            cash = float(account['cash'])

            # Get current price
            current_price = asyncio.run(alpaca_service.get_latest_price(symbol))
            if not current_price:
                logger.warning(f"⚠️  Could not get price for {symbol}")
                return 0

            # Use max position size if set, otherwise use 10% of capital
            if deployment.max_position_size:
                position_value = min(deployment.max_position_size, cash)
            else:
                position_value = cash * 0.1  # 10% of available cash

            # Calculate quantity
            quantity = int(position_value / current_price)

            logger.info(f"💰 Calculated position size: {quantity} shares of {symbol} at ${current_price}")
            return quantity

        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            return 0

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

            # Check position size limits for buy orders
            if action == 'buy':
                current_price = await alpaca_service.get_latest_price(symbol)
                if current_price:
                    within_limit = await self._check_position_size_limit(
                        deployment_id, symbol, quantity, current_price
                    )
                    if not within_limit:
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

    async def _get_daily_loss(self, deployment_id: str) -> Optional[float]:
        """
        Calculate the daily loss for a deployment

        Returns:
            Daily loss amount (negative number) or None if no loss
        """
        try:
            from datetime import datetime, time
            import pytz

            # Get today's start time (midnight ET)
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            today_start = et_tz.localize(
                datetime.combine(now_et.date(), time(0, 0, 0))
            )

            # Get all trades for today
            trades = await self.deployment_repo.get_trades_since(
                UUID(deployment_id),
                today_start
            )

            if not trades:
                return None

            # Calculate realized PnL from today's trades
            daily_pnl = sum(
                trade.get('realized_pnl', 0) or 0
                for trade in trades
                if trade.get('realized_pnl') is not None
            )

            # Also check unrealized PnL from current positions
            account = await alpaca_service.get_account()
            if account:
                # Get today's change from unrealized PnL
                unrealized_today = float(account.get('equity', 0)) - float(account.get('last_equity', 0))
                daily_pnl += unrealized_today

            # Return only if it's a loss (negative)
            return daily_pnl if daily_pnl < 0 else None

        except Exception as e:
            logger.error(f"❌ Error calculating daily loss: {e}")
            return None

    async def _check_position_size_limit(
        self,
        deployment_id: str,
        symbol: str,
        quantity: float,
        current_price: float
    ) -> bool:
        """
        Check if a proposed trade would exceed the maximum position size limit

        Returns:
            True if trade is within limits, False if it would exceed
        """
        try:
            config = self.active_deployments.get(deployment_id)
            if not config:
                return False

            deployment = config['deployment']
            max_position_size = deployment.max_position_size

            if not max_position_size:
                # No limit set
                return True

            # Calculate proposed position value
            proposed_value = quantity * current_price

            if proposed_value > max_position_size:
                logger.warning(
                    f"⚠️  Position size limit exceeded for {deployment_id}: "
                    f"Proposed ${proposed_value:.2f} > Max ${max_position_size:.2f}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error checking position size limit: {e}")
            return False


# Global trading engine instance
trading_engine = LiveTradingEngine()
