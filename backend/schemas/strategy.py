"""
Strategy Schema - Pydantic v2 models for trading strategy validation

This module defines strict schemas for all strategy components with:
- Automatic unit normalization (percentage -> decimal)
- Comprehensive validation
- Clear error messages
- Type safety throughout the pipeline

Example usage:
    from schemas.strategy import StrategySchema

    # Parse and validate a strategy dict
    strategy = StrategySchema.model_validate(raw_strategy_dict)

    # Access normalized values
    print(strategy.exit_conditions.stop_loss)  # Always decimal (0.10, not -10.0)
"""

import logging
from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

logger = logging.getLogger(__name__)


class EntrySignalType(str, Enum):
    """Supported entry signal types"""
    RSI = "rsi"
    MACD = "macd"
    SMA = "sma"
    SENTIMENT = "sentiment"
    NEWS = "news"
    PRICE = "price"
    PRICE_BASED = "price_based"
    CUSTOM = "custom"


class AllocationStrategy(str, Enum):
    """Portfolio allocation strategies"""
    EQUAL = "equal"
    SIGNAL_WEIGHTED = "signal_weighted"
    DYNAMIC_TRENDING = "dynamic_trending"
    MARKET_CAP_WEIGHTED = "market_cap_weighted"


class EntryConditionParameters(BaseModel):
    """Parameters for entry conditions"""
    # RSI parameters
    threshold: Optional[float] = Field(default=30, description="RSI threshold for entry")
    rsi_threshold: Optional[float] = Field(default=None, description="Alias for threshold")
    rsi_exit_threshold: Optional[float] = Field(default=70, description="RSI threshold for exit")
    comparison: Optional[str] = Field(default="below", description="Comparison type: below or above")

    # SMA parameters
    short_period: Optional[int] = Field(default=20, description="Short SMA period")
    long_period: Optional[int] = Field(default=50, description="Long SMA period")
    sma_short: Optional[int] = Field(default=None, description="Alias for short_period")
    sma_long: Optional[int] = Field(default=None, description="Alias for long_period")

    # MACD parameters
    crossover: Optional[str] = Field(default="bullish", description="MACD crossover type")

    # Sentiment parameters
    source: Optional[str] = Field(default="twitter", description="Sentiment source: twitter, reddit")
    sentiment_threshold: Optional[float] = Field(default=0.1, description="Sentiment threshold")

    # Price parameters
    trigger: Optional[str] = Field(default="any", description="Price trigger type")

    model_config = ConfigDict(extra="allow")  # Allow additional parameters


class EntryConditions(BaseModel):
    """Entry conditions for a trading strategy"""
    signal: EntrySignalType = Field(default=EntrySignalType.PRICE_BASED, description="Entry signal type")
    description: Optional[str] = Field(default="", description="Human-readable description")
    parameters: EntryConditionParameters = Field(default_factory=EntryConditionParameters)

    @field_validator('signal', mode='before')
    @classmethod
    def normalize_signal_type(cls, v):
        """Normalize signal type to enum"""
        if isinstance(v, str):
            v = v.lower().strip()
            # Handle aliases
            if v in ("price_based", "price-based"):
                return EntrySignalType.PRICE_BASED
            try:
                return EntrySignalType(v)
            except ValueError:
                logger.warning(f"Unknown signal type '{v}', defaulting to 'custom'")
                return EntrySignalType.CUSTOM
        return v


class ExitConditions(BaseModel):
    """
    Exit conditions for a trading strategy

    IMPORTANT: All percentage values are normalized to decimals:
    - Input: -10.0 (meaning -10%) -> Stored as: 0.10
    - Input: 0.10 -> Stored as: 0.10
    - Input: 10 (meaning 10%) -> Stored as: 0.10
    """
    take_profit: Optional[float] = Field(
        default=None,
        description="Take profit threshold (decimal, e.g., 0.02 for 2%)"
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Stop loss threshold (decimal, e.g., 0.10 for 10%)"
    )
    take_profit_pct_shares: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Fraction of position to sell at take profit (0.0-1.0)"
    )
    stop_loss_pct_shares: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Fraction of position to sell at stop loss (0.0-1.0)"
    )
    custom_exit: Optional[str] = Field(
        default=None,
        description="Custom exit condition description (e.g., 'RSI above 70')"
    )

    @field_validator('take_profit', mode='before')
    @classmethod
    def normalize_take_profit(cls, v):
        """Normalize take profit to positive decimal"""
        if v is None or v == 0:
            return None
        v = abs(float(v))
        # Convert percentage to decimal if > 1 (e.g., 10.0 -> 0.10)
        if v > 1:
            logger.info(f"Normalizing take_profit from {v}% to {v/100:.4f} decimal")
            v = v / 100.0
        return v

    @field_validator('stop_loss', mode='before')
    @classmethod
    def normalize_stop_loss(cls, v):
        """Normalize stop loss to positive decimal"""
        if v is None or v == 0:
            return None
        v = abs(float(v))
        # Convert percentage to decimal if > 1 (e.g., 10.0 -> 0.10)
        if v > 1:
            logger.info(f"Normalizing stop_loss from {v}% to {v/100:.4f} decimal")
            v = v / 100.0
        return v

    @field_validator('take_profit_pct_shares', 'stop_loss_pct_shares', mode='before')
    @classmethod
    def normalize_pct_shares(cls, v):
        """Ensure pct_shares is between 0 and 1"""
        if v is None:
            return 1.0
        v = float(v)
        if v < 0:
            return 0.0
        if v > 1:
            # Assume it's a percentage if > 1
            logger.info(f"Normalizing pct_shares from {v}% to {v/100:.4f}")
            return v / 100.0
        return v

    @property
    def has_trailing_stop(self) -> bool:
        """Check if this is a two-phase trailing stop strategy"""
        return (
            self.stop_loss is not None and
            self.stop_loss > 0 and
            self.take_profit_pct_shares < 1.0
        )

    @property
    def is_partial_exit_strategy(self) -> bool:
        """Check if strategy uses partial exits"""
        return self.take_profit_pct_shares < 1.0 or self.stop_loss_pct_shares < 1.0


class RiskManagement(BaseModel):
    """Risk management settings for a trading strategy"""
    position_size: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Position size as fraction of capital (0.0-1.0)"
    )
    max_positions: int = Field(
        default=1,
        ge=1,
        description="Maximum number of concurrent positions"
    )
    allocation: AllocationStrategy = Field(
        default=AllocationStrategy.EQUAL,
        description="Portfolio allocation strategy"
    )
    dynamic_selection: bool = Field(
        default=False,
        description="Whether to dynamically select stocks based on signals"
    )
    top_n: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of top stocks to select for dynamic strategies"
    )

    @field_validator('allocation', mode='before')
    @classmethod
    def normalize_allocation(cls, v):
        """Normalize allocation strategy to enum"""
        if isinstance(v, str):
            v = v.lower().strip().replace("-", "_")
            try:
                return AllocationStrategy(v)
            except ValueError:
                logger.warning(f"Unknown allocation strategy '{v}', defaulting to 'equal'")
                return AllocationStrategy.EQUAL
        return v

    @field_validator('position_size', mode='before')
    @classmethod
    def normalize_position_size(cls, v):
        """Normalize position size to 0-1 range"""
        if v is None:
            return 1.0
        v = float(v)
        if v > 1:
            # Assume it's a percentage
            return v / 100.0
        return max(0.0, min(1.0, v))


class StrategySchema(BaseModel):
    """
    Complete trading strategy schema with validation and normalization

    This is the single source of truth for strategy data structure.
    All components (generator, parser, backtester) must use this schema.

    Example:
        >>> raw = {
        ...     "name": "RSI Mean Reversion",
        ...     "asset": "AAPL",
        ...     "exit_conditions": {
        ...         "stop_loss": -10.0,  # Will be normalized to 0.10
        ...         "take_profit_pct_shares": 0.5
        ...     }
        ... }
        >>> strategy = StrategySchema.model_validate(raw)
        >>> strategy.exit_conditions.stop_loss
        0.1
        >>> strategy.exit_conditions.has_trailing_stop
        True
    """
    name: str = Field(description="Strategy name")
    description: Optional[str] = Field(default="", description="Strategy description")

    # Asset configuration
    asset: Optional[str] = Field(default="SPY", description="Primary trading asset")
    assets: Optional[List[str]] = Field(default=None, description="List of assets for portfolio mode")
    portfolio_mode: bool = Field(default=False, description="Whether to trade multiple assets")

    # Conditions
    entry_conditions: EntryConditions = Field(default_factory=EntryConditions)
    exit_conditions: ExitConditions = Field(default_factory=ExitConditions)

    # Risk management
    risk_management: RiskManagement = Field(default_factory=RiskManagement)

    # Data sources
    data_sources: List[str] = Field(
        default_factory=lambda: ["price"],
        description="Data sources used by the strategy"
    )

    @model_validator(mode='before')
    @classmethod
    def handle_nested_dicts(cls, data: Any) -> Any:
        """Handle nested dictionaries and ensure proper structure"""
        if isinstance(data, dict):
            # Ensure entry_conditions is properly structured
            if 'entry_conditions' in data and isinstance(data['entry_conditions'], dict):
                ec = data['entry_conditions']
                # If it has 'signal' at top level, wrap parameters
                if 'parameters' not in ec:
                    params = {k: v for k, v in ec.items() if k not in ('signal', 'description')}
                    ec['parameters'] = params

            # Ensure exit_conditions exists
            if 'exit_conditions' not in data:
                data['exit_conditions'] = {}

            # Ensure risk_management exists
            if 'risk_management' not in data:
                data['risk_management'] = {}

        return data

    @model_validator(mode='after')
    def validate_portfolio_mode(self):
        """Validate portfolio mode configuration"""
        if self.portfolio_mode:
            if not self.assets and not self.risk_management.dynamic_selection:
                logger.warning("Portfolio mode enabled but no assets specified and dynamic_selection is False")
        return self

    @property
    def is_two_phase_exit(self) -> bool:
        """Check if strategy uses two-phase exit (partial exit + trailing stop)"""
        return self.exit_conditions.has_trailing_stop

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility"""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: dict) -> "StrategySchema":
        """Create from dictionary with validation"""
        return cls.model_validate(data)

    def get_summary(self) -> str:
        """Get a human-readable summary of the strategy"""
        parts = [f"Strategy: {self.name}"]

        if self.portfolio_mode:
            parts.append(f"Assets: {', '.join(self.assets or ['dynamic'])}")
        else:
            parts.append(f"Asset: {self.asset}")

        parts.append(f"Entry: {self.entry_conditions.signal.value}")

        if self.exit_conditions.custom_exit:
            parts.append(f"Exit: {self.exit_conditions.custom_exit}")

        if self.exit_conditions.stop_loss:
            parts.append(f"Stop Loss: {self.exit_conditions.stop_loss*100:.1f}%")

        if self.exit_conditions.take_profit:
            parts.append(f"Take Profit: {self.exit_conditions.take_profit*100:.1f}%")

        if self.is_two_phase_exit:
            parts.append(f"Two-Phase Exit: Sell {self.exit_conditions.take_profit_pct_shares*100:.0f}%, then trailing stop")

        return " | ".join(parts)


# Convenience function for validation
def validate_strategy(raw_strategy: dict) -> StrategySchema:
    """
    Validate and normalize a raw strategy dictionary

    Args:
        raw_strategy: Dictionary containing strategy parameters

    Returns:
        Validated StrategySchema instance

    Raises:
        ValidationError: If strategy fails validation
    """
    return StrategySchema.model_validate(raw_strategy)
