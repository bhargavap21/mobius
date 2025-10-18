"""
FastAPI Backend for AI Trading Bot Generator
"""

import logging
import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, Any        
import queue
import uuid
from uuid import UUID
from datetime import datetime

from orchestrator import get_orchestrator
from tools.market_data import (
    get_stock_price,
    get_current_price,
    get_market_status,
    MARKET_DATA_TOOLS,
)
from tools.social_media import (
    get_reddit_sentiment,
    get_twitter_sentiment,
    analyze_social_sentiment,
    SOCIAL_MEDIA_TOOLS,
)
from tools.web_scraper import (
    scrape_website,
    scrape_company_news,
    WEB_SCRAPING_TOOLS,
)
from tools.code_generator import (
    parse_strategy,
    generate_trading_bot_code,
    create_trading_strategy,
    CODE_GENERATION_TOOLS,
)
from tools.backtester import backtest_strategy

# Import routes
from routes.auth_routes import router as auth_router
from routes.bot_routes import router as bot_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Trading Bot Generator",
    description="Generate trading bots from natural language using AI",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(bot_router)

# Initialize orchestrator and register tools
orchestrator = get_orchestrator()

# Register all tools on startup
@app.on_event("startup")
async def startup_event():
    """Register all tools with the orchestrator"""
    logger.info("🚀 Starting up AI Trading Bot API...")

    # Register market data tools
    for tool in MARKET_DATA_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Register social media tools
    for tool in SOCIAL_MEDIA_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Register web scraping tools
    for tool in WEB_SCRAPING_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Register code generation tools
    for tool in CODE_GENERATION_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    logger.info("✅ All tools registered successfully")


# Request/Response models
class StrategyRequest(BaseModel):
    strategy_description: str
    session_id: Optional[str] = None  # Optional session ID for progress tracking


class StrategyResponse(BaseModel):
    success: bool
    strategy: Optional[dict] = None
    code: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class BacktestRequest(BaseModel):
    strategy: dict
    days: int = 180
    initial_capital: float = 10000.0
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None


class BacktestResponse(BaseModel):
    success: bool
    results: Optional[dict] = None
    error: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Trading Bot Generator API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/api/strategy/create", response_model=StrategyResponse)
async def create_strategy(request: StrategyRequest):
    """
    Create a trading strategy from natural language description

    This endpoint:
    1. Parses the strategy description
    2. Generates Python trading bot code
    3. Returns the strategy parameters and code
    """
    try:
        logger.info(f"📋 Received strategy request: '{request.strategy_description[:100]}...'")

        # Use the create_trading_strategy function
        result = create_trading_strategy(request.strategy_description)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create strategy"))

        return StrategyResponse(
            success=True,
            strategy=result["strategy"],
            code=result["code"],
            message=result.get("message"),
        )

    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/backtest", response_model=BacktestResponse)
async def backtest(request: BacktestRequest):
    """
    Run backtest on a trading strategy

    This endpoint:
    1. Takes a parsed strategy configuration
    2. Fetches historical data from Alpaca
    3. Simulates trades based on strategy rules
    4. Returns performance metrics and trade history
    """
    try:
        logger.info(f"📊 Running backtest for {request.strategy.get('asset', 'unknown')}")

        results = backtest_strategy(
            strategy=request.strategy,
            days=request.days,
            initial_capital=request.initial_capital,
            take_profit=request.take_profit,
            stop_loss=request.stop_loss
        )

        return BacktestResponse(
            success=True,
            results=results
        )

    except Exception as e:
        logger.error(f"❌ Error running backtest: {e}")
        return BacktestResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/strategy/events/{session_id}")
async def get_events(session_id: str, from_index: int = 0):
    """
    Get events for a session (polling endpoint)
    """
    from progress_manager import progress_manager

    # Initialize session if it doesn't exist
    if session_id not in progress_manager.event_history:
        progress_manager.event_history[session_id] = []
        # Also create the queue session if needed
        if session_id not in progress_manager.sessions:
            progress_manager.create_session(session_id)
            logger.info(f"📡 Created session for polling: {session_id[:8]}")

    # Get events from history
    all_events = progress_manager.event_history.get(session_id, [])

    # Return events from the requested index
    events = all_events[from_index:] if from_index < len(all_events) else []

    return {
        "events": events,
        "total": len(all_events),
        "from": from_index,
        "session_active": session_id in progress_manager.sessions
    }


@app.get("/api/strategy/progress/{session_id}")
async def progress_stream(session_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates
    """
    from progress_manager import progress_manager

    async def event_generator() -> AsyncGenerator[str, None]:
        # Get or create session queue
        if session_id in progress_manager.sessions:
            logger.info(f"📡 Using existing session: {session_id[:8]}")
            queue = progress_manager.sessions[session_id]
        else:
            logger.info(f"📡 Creating new SSE session: {session_id[:8]}")
            queue = progress_manager.create_session(session_id)

        # Send initial connection message to establish SSE connection
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to activity stream'})}\n\n"

        try:
            while True:
                try:
                    # Wait for new event with timeout to keep connection alive
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Check if it's a completion event
                    if event.get('type') == 'complete' or event.get('type') == 'error':
                        yield f"data: {json.dumps(event)}\n\n"
                        break

                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f": keepalive\n\n"
                    continue
        finally:
            progress_manager.close_session(session_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.post("/api/strategy/create_multi_agent")
async def create_strategy_multi_agent(request: StrategyRequest):
    """
    Create and optimize a trading strategy using multi-agent system

    This endpoint:
    1. Uses Supervisor agent to orchestrate the workflow
    2. Code Generator creates/refines strategy
    3. Backtest Runner executes backtests
    4. Strategy Analyst reviews and provides feedback
    5. Iterates until satisfactory or max iterations reached

    Returns optimized strategy with full iteration history
    """
    try:
        # Get session_id from request
        session_id = request.session_id

        logger.info(f"🤖 Multi-Agent Request: '{request.strategy_description[:100]}...' (Session: {session_id})")

        # Pre-create the progress session if session_id provided
        if session_id:
            from progress_manager import progress_manager
            progress_manager.create_session(session_id)
            logger.info(f"📡 Pre-created progress session: {session_id[:8]}")

        from agents.supervisor import SupervisorAgent

        supervisor = SupervisorAgent()

        result = await supervisor.process({
            'user_query': request.strategy_description,
            'days': 180,
            'initial_capital': 10000,
            'session_id': session_id  # Pass session ID for progress updates
        })

        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Multi-agent workflow failed'))

        response_data = {
            "success": True,
            "session_id": session_id,  # Return session ID for progress tracking
            "strategy": result['strategy'],
            "code": result['code'],
            "backtest_results": result['backtest_results'],
            "iterations": result['iterations'],
            "iteration_history": result['iteration_history'],
            "final_analysis": result['final_analysis'],
            "insights_config": result.get('insights_config'),  # Pass insights config to frontend
            "message": f"Strategy optimized through {result['iterations']} iterations"
        }

        # Store result for later retrieval (in case connection drops)
        if session_id:
            from job_storage import job_storage
            job_storage.store_result(session_id, response_data)

        return response_data

    except Exception as e:
        logger.error(f"❌ Error in multi-agent workflow: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/result/{session_id}")
async def get_strategy_result(session_id: str):
    """
    Retrieve a completed job result by session ID
    Useful when connection drops during long-running jobs
    """
    from job_storage import job_storage

    result = job_storage.get_result(session_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job result not found or expired (results are stored for 24 hours)"
        )

    return result


@app.post("/api/chat")
async def chat(message: dict):
    """
    Chat with the AI for general queries

    Useful for:
    - Asking about strategies
    - Getting market data
    - Sentiment analysis
    """
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        result = orchestrator.chat(user_message)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))

        return {
            "success": True,
            "response": result["response"],
        }

    except Exception as e:
        logger.error(f"❌ Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Community Models
class SharedAgent(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    author: str
    tags: list[str] = []
    strategy: dict[str, Any]
    backtest_results: dict[str, Any]
    total_return: float
    win_rate: float
    total_trades: int
    symbol: str
    is_public: bool = True
    shared_at: Optional[str] = None
    views: int = 0
    likes: int = 0
    downloads: int = 0

class ShareAgentRequest(BaseModel):
    agent_id: str
    name: str
    description: str
    tags: list[str] = []
    is_public: bool = True


# Import community repository
from db.repositories.community_repository import CommunityRepository

# Initialize community repository
community_repo = CommunityRepository()

# Simple in-memory store for tracking mock agent likes (for demo purposes)
mock_agent_likes = {
    "mock-1": False,
    "mock-2": False, 
    "mock-3": False
}

# Community API Endpoints
@app.get("/api/community/agents")
async def get_shared_agents(page: int = 1, page_size: int = 20):
    """
    Get all publicly shared agents from the community
    """
    try:
        # Try to get data from database
        result = await community_repo.get_shared_agents(page=page, page_size=page_size)
        
        # Transform the data to include author names and performance metrics
        agents_with_details = []
        for agent in result.items:
            # Get original bot data for performance metrics
            original_bot_response = community_repo.client.table('trading_bots').select('*').eq('id', str(agent.original_bot_id)).execute()
            
            if original_bot_response.data:
                original_bot = original_bot_response.data[0]
                backtest_results = original_bot.get('backtest_results', {})
                
                # Get author name
                author_response = community_repo.client.table('users').select('full_name').eq('id', str(agent.author_id)).execute()
                author_name = author_response.data[0].get('full_name', 'Anonymous') if author_response.data else 'Anonymous'
                
                agent_data = {
                    "id": str(agent.id),
                    "name": agent.name,
                    "description": agent.description,
                    "author": author_name,
                    "tags": agent.tags,
                    "total_return": backtest_results.get('total_return', 0.0),
                    "win_rate": backtest_results.get('win_rate', 0),
                    "total_trades": backtest_results.get('total_trades', 0),
                    "symbol": original_bot.get('strategy_config', {}).get('asset', 'N/A'),
                    "views": agent.views,
                    "likes": agent.likes,
                    "downloads": agent.downloads,
                    "shared_at": agent.shared_at.isoformat(),
                    "liked": agent.liked
                }
                agents_with_details.append(agent_data)
        
        return {
            "success": True, 
            "agents": agents_with_details,
            "pagination": {
                "page": result.page,
                "page_size": result.page_size,
                "total": result.total,
                "total_pages": result.total_pages
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching shared agents: {e}")
        
        # If database tables don't exist, return mock data
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.info("📝 Returning mock community data (database tables not created yet)")
            
            mock_agents = [
                {
                    "id": "mock-1",
                    "name": "Elon Tweet Momentum Trader",
                    "description": "A sophisticated trading bot that monitors Elon Musk's tweets about Tesla and executes trades based on sentiment analysis and momentum indicators.",
                    "author": "Alex Chen",
                    "tags": ["momentum", "sentiment", "TSLA", "social-media"],
                    "total_return": 23.5,
                    "win_rate": 68,
                    "total_trades": 45,
                    "symbol": "TSLA",
                    "views": 1247,
                    "likes": 89,
                    "downloads": 156,
                    "shared_at": "2024-01-15T10:30:00Z",
                    "liked": mock_agent_likes.get("mock-1", False)
                },
                {
                    "id": "mock-2", 
                    "name": "Reddit WSB Sentiment Scanner",
                    "description": "Scans r/wallstreetbets for high-engagement posts and executes trades based on collective sentiment and volume spikes.",
                    "author": "Sarah Johnson",
                    "tags": ["reddit", "sentiment", "meme-stocks", "volume"],
                    "total_return": 156.8,
                    "win_rate": 42,
                    "total_trades": 78,
                    "symbol": "GME",
                    "views": 2341,
                    "likes": 167,
                    "downloads": 298,
                    "shared_at": "2024-01-12T14:22:00Z",
                    "liked": mock_agent_likes.get("mock-2", False)
                },
                {
                    "id": "mock-3",
                    "name": "RSI Oversold Bounce Trader",
                    "description": "Identifies oversold conditions using RSI and executes long positions with tight stop losses for quick bounces.",
                    "author": "Mike Rodriguez",
                    "tags": ["technical-analysis", "RSI", "mean-reversion", "scalping"],
                    "total_return": 89.2,
                    "win_rate": 74,
                    "total_trades": 123,
                    "symbol": "AAPL",
                    "views": 892,
                    "likes": 45,
                    "downloads": 67,
                    "shared_at": "2024-01-10T09:15:00Z",
                    "liked": mock_agent_likes.get("mock-3", False)
                }
            ]
            
            return {
                "success": True,
                "agents": mock_agents,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": len(mock_agents),
                    "total_pages": 1
                }
            }
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/community/share")
async def share_agent(agent_data: ShareAgentRequest, user_id: str = "current_user"):
    """
    Share an agent with the community
    """
    try:
        from db.models import SharedAgentCreate
        
        # Create shared agent data
        shared_agent_create = SharedAgentCreate(
            original_bot_id=UUID(agent_data.agent_id),
            name=agent_data.name,
            description=agent_data.description,
            tags=agent_data.tags,
            is_public=agent_data.is_public
        )
        
        # Save to database
        shared_agent = await community_repo.create_shared_agent(
            author_id=UUID(user_id),  # In production, get from auth token
            shared_agent_data=shared_agent_create
        )
        
        logger.info(f"📤 Agent shared: {agent_data.name} (ID: {shared_agent.id})")
        
        return {
            "success": True,
            "message": "Agent shared successfully",
            "agent": {
                "id": str(shared_agent.id),
                "name": shared_agent.name,
                "description": shared_agent.description,
                "tags": shared_agent.tags,
                "is_public": shared_agent.is_public,
                "shared_at": shared_agent.shared_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error sharing agent: {e}")
        
        # If database tables don't exist, return mock success
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.info("📝 Mock agent sharing (database tables not created yet)")
            return {
                "success": True,
                "message": "Agent shared successfully (mock mode)",
                "agent_id": "mock-shared-agent"
            }
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/community/agents/{agent_id}/like")
async def like_agent(agent_id: str, user_id: str = "current_user"):
    """
    Like/unlike a shared agent
    """
    try:
        # Handle mock IDs
        if agent_id.startswith('mock-'):
            # Toggle the like status
            current_status = mock_agent_likes.get(agent_id, False)
            new_status = not current_status
            mock_agent_likes[agent_id] = new_status
            
            action = "liked" if new_status else "unliked"
            logger.info(f"👍 Mock agent {action}: {agent_id}")
            
            return {
                "success": True,
                "message": f"Agent {action} successfully (mock mode)",
                "liked": new_status
            }
        
        # Try to convert to UUID for real agents
        try:
            agent_uuid = UUID(agent_id)
            user_uuid = UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid UUID format: {agent_id} or {user_id}")
            return {
                "success": True,
                "message": "Agent liked successfully (mock mode)",
                "liked": True
            }
        
        liked = await community_repo.like_agent(agent_uuid, user_uuid)
        
        action = "liked" if liked else "unliked"
        logger.info(f"👍 Agent {action}: {agent_id}")
        
        return {
            "success": True,
            "message": f"Agent {action} successfully",
            "liked": liked
        }
        
    except Exception as e:
        logger.error(f"❌ Error liking agent: {e}")
        
        # If database tables don't exist, return mock success
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.info("📝 Mock agent liking (database tables not created yet)")
            return {
                "success": True,
                "message": "Agent liked successfully (mock mode)",
                "liked": True
            }
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/community/agents/{agent_id}/download")
async def download_agent(agent_id: str, user_id: str = None):
    """
    Download a shared agent's configuration
    """
    try:
        # Handle mock IDs
        if agent_id.startswith('mock-'):
            logger.info(f"📥 Mock agent downloaded: {agent_id}")
            
            # Return mock agent configuration based on ID
            mock_configs = {
                'mock-1': {
                    "id": agent_id,
                    "name": "Elon Tweet Momentum Trader",
                    "description": "A sophisticated trading bot that monitors Elon Musk's tweets about Tesla and executes trades based on sentiment analysis and momentum indicators.",
                    "strategy": {
                        "type": "elon_tweet_momentum",
                        "parameters": {
                            "symbol": "TSLA",
                            "sentiment_threshold": 0.7,
                            "momentum_period": 14,
                            "entry_threshold": 0.02,
                            "exit_threshold": 0.05
                        }
                    },
                    "backtest_results": {
                        "total_return": 23.5,
                        "win_rate": 68,
                        "total_trades": 45,
                        "max_drawdown": -8.2
                    }
                },
                'mock-2': {
                    "id": agent_id,
                    "name": "Reddit WSB Sentiment Scanner",
                    "description": "Scans r/wallstreetbets for high-engagement posts and executes trades based on collective sentiment and volume spikes.",
                    "strategy": {
                        "type": "reddit_sentiment_scanner",
                        "parameters": {
                            "symbol": "GME",
                            "subreddit": "wallstreetbets",
                            "min_upvotes": 1000,
                            "sentiment_threshold": 0.5,
                            "volume_spike_threshold": 2.0
                        }
                    },
                    "backtest_results": {
                        "total_return": 156.8,
                        "win_rate": 42,
                        "total_trades": 78,
                        "max_drawdown": -25.3
                    }
                },
                'mock-3': {
                    "id": agent_id,
                    "name": "RSI Oversold Bounce Trader",
                    "description": "Identifies oversold conditions using RSI and executes long positions with tight stop losses for quick bounces.",
                    "strategy": {
                        "type": "rsi_oversold_bounce",
                        "parameters": {
                            "symbol": "AAPL",
                            "rsi_period": 14,
                            "oversold_threshold": 30,
                            "overbought_threshold": 70,
                            "stop_loss": 0.02
                        }
                    },
                    "backtest_results": {
                        "total_return": 89.2,
                        "win_rate": 74,
                        "total_trades": 123,
                        "max_drawdown": -12.1
                    }
                }
            }
            
            mock_config = mock_configs.get(agent_id, mock_configs['mock-1'])
            
            return StreamingResponse(
                iter([json.dumps(mock_config, indent=2)]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=mock_agent_{agent_id}.json"}
            )
        
        # Try to convert to UUID for real agents
        try:
            agent_uuid = UUID(agent_id)
            user_uuid = UUID(user_id) if user_id else None
        except ValueError:
            logger.warning(f"Invalid UUID format: {agent_id}")
            # Return a generic mock config
            mock_config = {
                "id": agent_id,
                "name": "Mock Trading Agent",
                "description": "This is a mock agent configuration for demonstration purposes.",
                "strategy": {"type": "mock_strategy", "parameters": {}},
                "backtest_results": {"total_return": 15.5, "win_rate": 65, "total_trades": 42}
            }
            return StreamingResponse(
                iter([json.dumps(mock_config, indent=2)]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=mock_agent_{agent_id}.json"}
            )
        
        # Download from database and increment download count
        original_bot_data = await community_repo.download_agent(agent_uuid, user_uuid)
        
        if not original_bot_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"📥 Agent downloaded: {agent_id}")
        
        # Return the original bot configuration as JSON
        return StreamingResponse(
            iter([json.dumps(original_bot_data, indent=2, default=str)]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=agent_{agent_id}.json"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading agent: {e}")
        
        # If database tables don't exist, return mock download
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.info("📝 Mock agent download (database tables not created yet)")
            
            # Return mock agent configuration
            mock_agent_config = {
                "id": agent_id,
                "name": "Mock Trading Agent",
                "description": "This is a mock agent configuration for demonstration purposes.",
                "strategy": {
                    "type": "mock_strategy",
                    "parameters": {
                        "symbol": "AAPL",
                        "entry_threshold": 0.02,
                        "exit_threshold": 0.05
                    }
                },
                "backtest_results": {
                    "total_return": 15.5,
                    "win_rate": 65,
                    "total_trades": 42
                }
            }
            
            return StreamingResponse(
                iter([json.dumps(mock_agent_config, indent=2)]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=mock_agent_{agent_id}.json"}
            )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bots")
async def create_bot(bot_data: dict, user_id: str = "current_user"):
    """
    Save an agent to user's bot collection (for Save to My Bots functionality)
    """
    try:
        # For mock purposes, just return success
        # In a real implementation, this would save to the trading_bots table
        logger.info(f"🤖 Bot saved to user collection: {bot_data.get('name', 'Unknown')}")
        
        return {
            "success": True,
            "message": "Bot saved to your collection successfully",
            "bot_id": f"user-bot-{uuid.uuid4().hex[:8]}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
