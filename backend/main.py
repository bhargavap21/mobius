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
from typing import Optional, AsyncGenerator
import queue

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
