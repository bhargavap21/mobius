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
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

    # Summary from backtest results
    total_trades: Optional[int] = None
    total_return: Optional[float] = None
    win_rate: Optional[float] = None


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
