"""
Pydantic models for database entities
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# USER MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class User(UserBase):
    """Complete user model"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: UUID
    email: str
    full_name: Optional[str] = None
    created_at: datetime


# ============================================================================
# TRADING BOT MODELS
# ============================================================================

class TradingBotBase(BaseModel):
    """Base trading bot model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TradingBotCreate(TradingBotBase):
    """Model for creating a new trading bot"""
    strategy_config: Dict[str, Any]
    generated_code: str
    backtest_results: Optional[Dict[str, Any]] = None
    insights_config: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class TradingBotUpdate(BaseModel):
    """Model for updating a trading bot"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_favorite: Optional[bool] = None
    strategy_config: Optional[Dict[str, Any]] = None
    generated_code: Optional[str] = None
    backtest_results: Optional[Dict[str, Any]] = None
    insights_config: Optional[Dict[str, Any]] = None


class TradingBot(TradingBotBase):
    """Complete trading bot model"""
    id: UUID
    user_id: UUID
    strategy_config: Dict[str, Any]
    generated_code: str
    backtest_results: Optional[Dict[str, Any]] = None
    insights_config: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradingBotListItem(BaseModel):
    """Simplified trading bot model for list views"""
    id: UUID
    name: str
    description: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# COMMUNITY MODELS
# ============================================================================

class SharedAgentBase(BaseModel):
    """Base shared agent model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    tags: List[str] = Field(default_factory=list)
    is_public: bool = True


class SharedAgentCreate(SharedAgentBase):
    """Model for creating a shared agent"""
    original_bot_id: UUID


class SharedAgentUpdate(BaseModel):
    """Model for updating a shared agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class SharedAgent(SharedAgentBase):
    """Complete shared agent model"""
    id: UUID
    original_bot_id: UUID
    author_id: UUID
    views: int = 0
    likes: int = 0
    downloads: int = 0
    shared_at: datetime
    updated_at: datetime
    liked: bool = False  # Whether current user has liked this agent

    model_config = ConfigDict(from_attributes=True)


class SharedAgentListItem(BaseModel):
    """Simplified shared agent model for list views"""
    id: UUID
    name: str
    description: str
    author_id: UUID
    tags: List[str]
    views: int
    likes: int
    downloads: int
    shared_at: datetime
    liked: bool = False

    model_config = ConfigDict(from_attributes=True)


class AgentLike(BaseModel):
    """Model for agent likes"""
    id: UUID
    shared_agent_id: UUID
    user_id: UUID
    liked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentDownload(BaseModel):
    """Model for agent downloads"""
    id: UUID
    shared_agent_id: UUID
    user_id: Optional[UUID] = None
    downloaded_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple message response model"""
    message: str
    success: bool = True


# ============================================================================
# BOT EXECUTION MODELS
# ============================================================================

class BotExecutionCreate(BaseModel):
    """Model for creating a bot execution record"""
    bot_id: UUID
    status: str = Field(..., pattern="^(running|success|failed|cancelled)$")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BotExecutionUpdate(BaseModel):
    """Model for updating a bot execution"""
    status: Optional[str] = Field(None, pattern="^(running|success|failed|cancelled)$")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class BotExecution(BaseModel):
    """Complete bot execution model"""
    id: UUID
    bot_id: UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool


class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    email_confirmed: bool = False
    message: Optional[str] = None


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_more: bool = False
    
    def __init__(self, **data):
        # Calculate has_more based on page and total_pages
        if 'has_more' not in data:
            data['has_more'] = data.get('page', 1) < data.get('total_pages', 1)
        super().__init__(**data)
# ============================================================================
# DEPLOYMENT MODELS
# ============================================================================

class DeploymentCreate(BaseModel):
    """Model for creating a new deployment"""
    bot_id: UUID
    initial_capital: float = 10000.00
    execution_frequency: str = "5min"
    max_position_size: Optional[float] = None
    daily_loss_limit: Optional[float] = None


class DeploymentUpdate(BaseModel):
    """Model for updating a deployment"""
    status: Optional[str] = Field(None, pattern="^(running|paused|stopped|error)$")
    current_capital: Optional[float] = None
    total_pnl: Optional[float] = None
    total_return_pct: Optional[float] = None
    last_execution_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Deployment(BaseModel):
    """Complete deployment model"""
    id: UUID
    user_id: UUID
    bot_id: UUID
    status: str
    alpaca_account_id: Optional[str] = None
    initial_capital: float
    current_capital: Optional[float] = None
    total_pnl: float = 0.0
    total_return_pct: float = 0.0
    execution_frequency: str
    max_position_size: Optional[float] = None
    daily_loss_limit: Optional[float] = None
    deployed_at: datetime
    stopped_at: Optional[datetime] = None
    last_execution_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeploymentTrade(BaseModel):
    """Deployment trade record"""
    id: UUID
    deployment_id: UUID
    alpaca_order_id: Optional[str] = None
    alpaca_order_status: Optional[str] = None
    symbol: str
    side: str
    order_type: str = "market"
    quantity: float
    filled_qty: Optional[float] = None
    filled_avg_price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    total_value: Optional[float] = None
    commission: float = 0.0
    realized_pnl: Optional[float] = None
    submitted_at: datetime
    filled_at: Optional[datetime] = None
    signal_metadata: Dict[str, Any] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeploymentMetrics(BaseModel):
    """Deployment performance metrics snapshot"""
    id: UUID
    deployment_id: UUID
    timestamp: datetime
    portfolio_value: float
    cash: float
    positions_value: float
    total_return_pct: Optional[float] = None
    daily_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    open_positions_count: int = 0
    total_trades_count: int = 0
    winning_trades_count: int = 0
    losing_trades_count: int = 0
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class DeploymentPosition(BaseModel):
    """Current open position in a deployment"""
    id: UUID
    deployment_id: UUID
    symbol: str
    quantity: float
    average_entry_price: float
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    cost_basis: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None
    opened_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
