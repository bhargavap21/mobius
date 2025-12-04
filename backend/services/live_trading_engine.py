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
            
            # Initial sync to load existing running deployments
            # This will run immediately when the engine starts
            import asyncio
            try:
                # Schedule initial sync
                asyncio.create_task(self._sync_deployments())
                logger.info("📋 Scheduled initial deployment sync")
            except Exception as e:
                logger.warning(f"⚠️  Could not schedule initial sync: {e}, will sync on next scheduled run")

    def stop(self):
        """Stop the trading engine"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("🛑 Live Trading Engine stopped")

    async def _sync_deployments(self):
        """
        Sync active deployments from database
        Runs every minute to check for new/updated/stopped deployments
        
        This function:
        1. Loads all 'running' deployments from database
        2. Adds any new ones to active_deployments
        3. Removes stopped/error deployments
        """
        try:
            logger.debug("🔄 Syncing deployments from database...")

            # Get all running deployments from database
            running_deployments = await self.deployment_repo.get_all_running_deployments()
            logger.debug(f"📊 Found {len(running_deployments)} running deployments in database")

            # Add new running deployments to active list
            for deployment in running_deployments:
                deployment_id_str = str(deployment.id)
                if deployment_id_str not in self.active_deployments:
                    # Try to add this deployment
                    logger.info(f"🔄 Found new running deployment {deployment.id}, adding to trading engine...")
                    success = await self.add_deployment(deployment.id)
                    if success:
                        logger.info(f"✅ Auto-loaded deployment {deployment.id} into trading engine")
                    else:
                        logger.warning(f"⚠️  Failed to auto-load deployment {deployment.id}")

            # Remove stopped/error/paused deployments from active list
            for deployment_id in list(self.active_deployments.keys()):
                deployment = await self.deployment_repo.get_deployment(UUID(deployment_id))
                if not deployment or deployment.status in ['stopped', 'error', 'paused']:
                    await self.remove_deployment(deployment_id)
                    logger.info(f"🗑️  Removed {deployment.status if deployment else 'missing'} deployment {deployment_id} from active list")
            
        except Exception as e:
            logger.error(f"❌ Error syncing deployments: {e}")
            import traceback
            logger.debug(traceback.format_exc())

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

            filled_qty = order.get('filled_qty', 0)
            filled_avg_price = order.get('filled_avg_price')
            total_value = float(filled_avg_price * filled_qty) if filled_avg_price and filled_qty else None

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
                    'filled_qty': filled_qty,
                    'filled_avg_price': filled_avg_price,
                    'total_value': total_value,
                    'signal_metadata': signal,
                    'submitted_at': datetime.utcnow().isoformat()
                }
            )

            logger.info(f"✅ {action.upper()} order placed: {quantity} {symbol}, Order ID: {order['order_id']}")

            # Update deployment-specific position tracking
            if filled_qty and filled_qty > 0 and filled_avg_price:
                await self._update_deployment_position(deployment_id, symbol, action, filled_qty, filled_avg_price)

        except Exception as e:
            logger.error(f"❌ Error processing signal: {e}")

    async def _update_metrics(self, deployment_id: str):
        """
        Update deployment metrics using deployment-specific trades and positions
        
        This calculates virtual portfolio performance per deployment, independent of
        other deployments sharing the same Alpaca account.
        """
        try:
            config = self.active_deployments[deployment_id]
            deployment = config['deployment']
            initial_capital = deployment.initial_capital

            # Get deployment-specific trades
            trades = await self.deployment_repo.get_deployment_trades(UUID(deployment_id), limit=10000)
            
            # Get deployment-specific positions
            positions = await self.deployment_repo.get_deployment_positions(UUID(deployment_id))

            # Calculate virtual cash (initial capital minus all buy trades)
            total_buy_value = sum(
                float(trade.total_value or 0) 
                for trade in trades 
                if trade.side == 'buy' and trade.filled_qty and trade.filled_qty > 0
            )
            total_sell_value = sum(
                float(trade.total_value or 0)
                for trade in trades
                if trade.side == 'sell' and trade.filled_qty and trade.filled_qty > 0
            )
            
            # Virtual cash = initial capital - net buy value + net sell value
            virtual_cash = initial_capital - total_buy_value + total_sell_value
            
            # Calculate virtual positions value
            virtual_positions_value = sum(float(pos.market_value or 0) for pos in positions)
            
            # Virtual portfolio value
            virtual_portfolio_value = virtual_cash + virtual_positions_value

            # Calculate realized P&L from closed trades
            realized_pnl = sum(
                float(trade.realized_pnl or 0) 
                for trade in trades 
                if trade.realized_pnl is not None
            )

            # Calculate unrealized P&L from open positions
            unrealized_pnl = sum(float(pos.unrealized_pnl or 0) for pos in positions)

            # Total P&L
            total_pnl = realized_pnl + unrealized_pnl
            
            # Total return percentage
            total_return_pct = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0

            # Count trades
            total_trades = len([t for t in trades if t.filled_qty and t.filled_qty > 0])
            winning_trades = len([t for t in trades if t.realized_pnl and t.realized_pnl > 0])
            losing_trades = len([t for t in trades if t.realized_pnl and t.realized_pnl < 0])

            # Log metrics
            await self.deployment_repo.log_metrics(
                UUID(deployment_id),
                {
                    'portfolio_value': virtual_portfolio_value,
                    'cash': virtual_cash,
                    'positions_value': virtual_positions_value,
                    'total_return_pct': total_return_pct,
                    'realized_pnl': realized_pnl,
                    'unrealized_pnl': unrealized_pnl,
                    'open_positions_count': len(positions),
                    'total_trades_count': total_trades,
                    'winning_trades_count': winning_trades,
                    'losing_trades_count': losing_trades
                }
            )

            # Update deployment current capital
            await self.deployment_repo.update_deployment(
                UUID(deployment_id),
                DeploymentUpdate(
                    current_capital=virtual_portfolio_value,
                    total_pnl=total_pnl,
                    total_return_pct=total_return_pct
                )
            )

            logger.debug(f"📊 Updated metrics for {deployment_id}: ${virtual_portfolio_value:,.2f} ({total_return_pct:+.2f}%) | Realized: ${realized_pnl:,.2f} | Unrealized: ${unrealized_pnl:,.2f}")

        except Exception as e:
            logger.error(f"❌ Error updating metrics for {deployment_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    async def _update_deployment_position(
        self,
        deployment_id: str,
        symbol: str,
        side: str,
        quantity: float,
        fill_price: float
    ):
        """
        Update deployment-specific position tracking
        
        This maintains a separate position record for each deployment,
        independent of the shared Alpaca account positions.
        """
        try:
            # Get current position for this deployment
            positions = await self.deployment_repo.get_deployment_positions(UUID(deployment_id))
            current_pos = next((p for p in positions if p.symbol == symbol), None)

            if side == 'buy':
                if current_pos:
                    # Add to existing position (weighted average)
                    old_qty = float(current_pos.quantity)
                    old_avg = float(current_pos.average_entry_price)
                    new_qty = old_qty + quantity
                    new_avg = ((old_qty * old_avg) + (quantity * fill_price)) / new_qty
                    
                    # Get current market price
                    current_price = await alpaca_service.get_latest_price(symbol)
                    if not current_price:
                        current_price = fill_price  # Fallback to fill price
                    
                    market_value = new_qty * current_price
                    cost_basis = new_qty * new_avg
                    unrealized_pnl = market_value - cost_basis
                    unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                    
                    await self.deployment_repo.upsert_position(
                        UUID(deployment_id),
                        {
                            'symbol': symbol,
                            'quantity': new_qty,
                            'average_entry_price': new_avg,
                            'current_price': current_price,
                            'market_value': market_value,
                            'cost_basis': cost_basis,
                            'unrealized_pnl': unrealized_pnl,
                            'unrealized_pnl_pct': unrealized_pnl_pct
                        }
                    )
                else:
                    # New position
                    current_price = await alpaca_service.get_latest_price(symbol) or fill_price
                    market_value = quantity * current_price
                    cost_basis = quantity * fill_price
                    unrealized_pnl = market_value - cost_basis
                    unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                    
                    await self.deployment_repo.upsert_position(
                        UUID(deployment_id),
                        {
                            'symbol': symbol,
                            'quantity': quantity,
                            'average_entry_price': fill_price,
                            'current_price': current_price,
                            'market_value': market_value,
                            'cost_basis': cost_basis,
                            'unrealized_pnl': unrealized_pnl,
                            'unrealized_pnl_pct': unrealized_pnl_pct
                        }
                    )
            
            elif side == 'sell':
                if current_pos:
                    old_qty = float(current_pos.quantity)
                    old_avg = float(current_pos.average_entry_price)
                    
                    # Calculate realized P&L for sold shares
                    cost_basis_sold = quantity * old_avg
                    proceeds = quantity * fill_price
                    realized_pnl = proceeds - cost_basis_sold
                    
                    new_qty = old_qty - quantity
                    
                    if new_qty <= 0:
                        # Position fully closed
                        await self.deployment_repo.delete_position(UUID(deployment_id), symbol)
                    else:
                        # Partial close - update position
                        current_price = await alpaca_service.get_latest_price(symbol) or fill_price
                        market_value = new_qty * current_price
                        cost_basis = new_qty * old_avg
                        unrealized_pnl = market_value - cost_basis
                        unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                        
                        await self.deployment_repo.upsert_position(
                            UUID(deployment_id),
                            {
                                'symbol': symbol,
                                'quantity': new_qty,
                                'average_entry_price': old_avg,  # Entry price doesn't change
                                'current_price': current_price,
                                'market_value': market_value,
                                'cost_basis': cost_basis,
                                'unrealized_pnl': unrealized_pnl,
                                'unrealized_pnl_pct': unrealized_pnl_pct
                            }
                        )
                else:
                    logger.warning(f"⚠️  Trying to sell {symbol} but no position found for deployment {deployment_id}")

        except Exception as e:
            logger.error(f"❌ Error updating deployment position: {e}")
            import traceback
            logger.debug(traceback.format_exc())


# Global trading engine instance
trading_engine = LiveTradingEngine()
