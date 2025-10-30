"""
FastAPI Backend for AI Trading Bot Generator
"""

import logging
import asyncio
import json
from fastapi import FastAPI, HTTPException, Query, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, Any
import queue
import uuid
from uuid import UUID
from datetime import datetime
from middleware.auth_middleware import get_optional_user_id, get_current_user_id

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
from tools.politician_trades import (
    get_politician_trades,
    get_pelosi_portfolio_tickers,
    POLITICIAN_TRADING_TOOLS,
)

# Import routes
from routes.auth_routes import router as auth_router
from routes.bot_routes import router as bot_router
from routes.deployment_routes import router as deployment_router

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
app.include_router(deployment_router)

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

    # Register politician trading tools
    for tool in POLITICIAN_TRADING_TOOLS:
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


class RefineStrategyRequest(BaseModel):
    current_strategy: dict
    current_code: str
    refinement_instructions: str
    session_id: Optional[str] = None


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
async def backtest(
    request: BacktestRequest,
    user_id: Optional[UUID] = Depends(get_optional_user_id)
):
    """
    Run backtest on a trading strategy

    This endpoint:
    1. Takes a parsed strategy configuration
    2. Fetches historical data from Alpaca
    3. Simulates trades based on strategy rules
    4. Returns performance metrics and trade history
    5. Auto-saves to chat history
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

        # Auto-save to chat history after successful backtest
        if user_id:
            try:
                from db.repositories.bot_repository import BotRepository
                from db.models import TradingBotCreate
                import uuid

                bot_repo = BotRepository()

                # Create auto-saved bot entry
                bot_data = TradingBotCreate(
                    name=request.strategy.get('name', 'Untitled Strategy'),
                    description=request.strategy.get('description', ''),
                    strategy_config=request.strategy,
                    generated_code="",  # Not available at backtest stage
                    backtest_results=results,
                    session_id=request.session_id if hasattr(request, 'session_id') else str(uuid.uuid4()),
                    is_saved=False  # Auto-saved, not manually saved
                )

                await bot_repo.create(user_id=user_id, bot_data=bot_data)
                logger.info(f"✅ Auto-saved strategy to chat history for user {user_id}")
            except Exception as save_error:
                logger.error(f"⚠️ Failed to auto-save strategy: {save_error}")
                # Don't fail the backtest if auto-save fails

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
async def get_events(session_id: str, from_: int = Query(0, alias="from")):
    """
    Get events for a session (polling endpoint)
    """
    from progress_manager import progress_manager

    logger.info(f"📡 Polling request: session={session_id[:8]}, from={from_}")
    logger.info(f"📡 Available sessions: {list(progress_manager.event_history.keys())}")

    # Initialize session if it doesn't exist
    if session_id not in progress_manager.event_history:
        logger.warning(f"⚠️ Session {session_id[:8]} not found in event_history, creating empty...")
        progress_manager.event_history[session_id] = []
        # Also create the queue session if needed
        if session_id not in progress_manager.sessions:
            progress_manager.create_session(session_id)
            logger.info(f"📡 Created session for polling: {session_id[:8]}")

    # Get events from history
    all_events = progress_manager.event_history.get(session_id, [])
    logger.info(f"📡 Total events for session {session_id[:8]}: {len(all_events)}")

    # Return events from the requested index
    events = all_events[from_:] if from_ < len(all_events) else []
    logger.info(f"📡 Returning {len(events)} events (from index {from_})")

    return {
        "events": events,
        "total": len(all_events),
        "from": from_,
        "session_active": session_id in progress_manager.sessions
    }


async def _run_multi_agent_workflow(
    session_id: str,
    strategy_description: str,
    fast_mode: bool,
    user_id: UUID
):
    """
    Helper function to run the multi-agent workflow
    This can be called from both the new two-step flow and legacy endpoint
    """
    try:
        logger.info(f"🤖 Multi-Agent Workflow Starting: '{strategy_description[:100]}...' (Session: {session_id})")

        from agents.supervisor import SupervisorAgent
        from db.repositories.bot_repository import BotRepository
        from db.models import TradingBotCreate
        from job_storage import job_storage

        supervisor = SupervisorAgent()

        # Adjust parameters based on fast mode
        days = 30 if fast_mode else 90
        initial_capital = 10000

        result = await supervisor.process({
            'user_query': strategy_description,
            'days': days,
            'initial_capital': initial_capital,
            'session_id': session_id,
            'fast_mode': fast_mode
        })

        if not result.get('success'):
            error_data = {
                "success": False,
                "error": result.get('error', 'Multi-agent workflow failed')
            }
            job_storage.store_result(session_id, error_data)

            # Emit error complete event AFTER storing result
            from progress_manager import progress_manager
            if progress_manager:
                await progress_manager.emit_event(session_id, {
                    'type': 'error',
                    'agent': 'Supervisor',
                    'action': 'Workflow failed',
                    'message': error_data['error'],
                    'icon': '❌'
                })
            return

        response_data = {
            "success": True,
            "session_id": session_id,
            "strategy": result['strategy'],
            "code": result['code'],
            "backtest_results": result['backtest_results'],
            "iterations": result['iterations'],
            "iteration_history": result['iteration_history'],
            "final_analysis": result['final_analysis'],
            "insights_config": result.get('insights_config'),
            "message": f"Strategy optimized through {result['iterations']} iterations"
        }

        # ARCHITECTURAL FIX: Store result and emit complete event BEFORE slow database save
        # This prevents WebSocket timeout (30s) from firing during database operations

        # Store result in job_storage IMMEDIATELY (this is fast, synchronous)
        job_storage.store_result(session_id, response_data)
        logger.info(f"💾 Result stored in job_storage for session {session_id[:8]}")

        # Emit complete event IMMEDIATELY (before slow database operations)
        from progress_manager import progress_manager
        if progress_manager:
            await progress_manager.emit_complete(session_id, result['iterations'])
            logger.info(f"✅ Complete event emitted for session {session_id[:8]}")
            # Small yield to let WebSocket grab the event from queue
            await asyncio.sleep(0.05)

        # NOW do slow database operations in background (don't block WebSocket)
        async def save_to_database():
            """Background task to save strategy to database"""
            try:
                bot_repo = BotRepository()
                bot_data = TradingBotCreate(
                    name=result['strategy'].get('name', 'Untitled Strategy'),
                    description=strategy_description[:200] if len(strategy_description) > 200 else strategy_description,
                    strategy_config=result['strategy'],
                    generated_code=result['code'],
                    backtest_results=result['backtest_results'],
                    insights_config=result.get('insights_config'),
                    session_id=session_id,
                    is_saved=False
                )
                await bot_repo.create(user_id=user_id, bot_data=bot_data)
                logger.info(f"✅ Auto-saved strategy to chat history for user {user_id}")
            except Exception as save_error:
                logger.error(f"⚠️ Failed to auto-save strategy: {save_error}")

        # Run database save in background - don't wait for it
        asyncio.create_task(save_to_database())
        logger.info(f"🔄 Database save running in background for session {session_id[:8]}")

        logger.info(f"✅ Workflow complete for session {session_id[:8]}")

    except Exception as e:
        logger.error(f"❌ Error in multi-agent workflow: {e}")
        import traceback
        traceback.print_exc()

        error_data = {
            "success": False,
            "error": str(e)
        }
        from job_storage import job_storage
        job_storage.store_result(session_id, error_data)

        # CRITICAL: Emit error event to WebSocket so client knows workflow failed
        from progress_manager import progress_manager
        if progress_manager:
            await progress_manager.emit_error(session_id, 'Workflow', str(e))
            logger.info(f"✅ Error event emitted for session {session_id[:8]}")


@app.post("/api/sessions")
async def create_session(user_id: UUID = Depends(get_current_user_id)):
    """
    Step 1: Create a session (no work starts yet)
    Returns a session_id for the client to open SSE and then start workflow
    """
    from progress_manager import progress_manager

    session_id = str(uuid.uuid4())
    # Pre-create the session and event history
    progress_manager.create_session(session_id)

    logger.info(f"📡 Created session {session_id[:8]} for user {user_id}")

    return {"sessionId": session_id}


@app.websocket("/ws/strategy/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time progress updates
    Step 2: Client connects to this BEFORE starting the workflow
    """
    from progress_manager import progress_manager

    await websocket.accept()
    logger.info(f"🔌 WebSocket client connected for session: {session_id[:8]}")

    try:
        # Get or create session queue
        if session_id in progress_manager.sessions:
            logger.info(f"📡 WS client connected to existing session: {session_id[:8]}")
            queue = progress_manager.sessions[session_id]
        else:
            logger.info(f"📡 Creating new WS session: {session_id[:8]}")
            queue = progress_manager.create_session(session_id)

        # Send buffered events first (if any)
        if session_id in progress_manager.event_history:
            logger.info(f"📡 Sending {len(progress_manager.event_history[session_id])} buffered events")
            for event in progress_manager.event_history[session_id]:
                await websocket.send_json(event)

        # Send ready signal
        await websocket.send_json({
            'type': 'ready',
            'message': 'Stream ready, you can start the workflow'
        })
        logger.info(f"✅ Sent ready signal for session: {session_id[:8]}")

        # Stream events as they arrive
        logger.info(f"🔄 Entering event loop for session: {session_id[:8]}")
        while True:
            try:
                # Wait for new event with timeout
                import time
                wait_start = time.time()
                logger.debug(f"⏳ Waiting for event from queue (session: {session_id[:8]}, qsize: {queue.qsize()})")
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                wait_end = time.time()
                logger.info(f"📦 Retrieved event from queue: {event.get('type')} at {wait_end}, waited {wait_end - wait_start:.3f}s (session: {session_id[:8]})")

                # Send event to client - explicitly catch connection errors
                logger.info(f"🔜 About to send event: {event.get('type')} (session: {session_id[:8]})")
                try:
                    await websocket.send_json(event)
                    logger.info(f"📤 Sent event to WS client: {event.get('type')} - {event.get('message', '')} (session: {session_id[:8]})")
                except WebSocketDisconnect as ws_disc:
                    logger.warning(f"⚠️ Client disconnected while sending event: {event.get('type')} - {ws_disc} (session: {session_id[:8]})")
                    raise  # Re-raise to exit the loop
                except Exception as send_error:
                    logger.error(f"❌ Error sending event to client: {type(send_error).__name__}: {send_error} (session: {session_id[:8]})")
                    import traceback
                    traceback.print_exc()
                    raise

                # Check if it's a completion event
                if event.get('type') in ['complete', 'error']:
                    # CRITICAL: Give the client time to receive the complete event before closing
                    # Without this delay, we close the connection immediately after sending,
                    # and the client may not receive the event due to network buffering
                    logger.info(f"⏸️  Sent complete event, waiting briefly before closing (session: {session_id[:8]})")
                    await asyncio.sleep(0.5)  # Wait 500ms to ensure client receives the event
                    logger.info(f"🎉 Workflow complete, closing WS for session: {session_id[:8]}")
                    break

            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                logger.debug(f"💓 Sending heartbeat (session: {session_id[:8]})")
                try:
                    await websocket.send_json({'type': 'heartbeat'})
                except Exception as heartbeat_error:
                    logger.warning(f"⚠️ Failed to send heartbeat, client may have disconnected: {heartbeat_error}")
                    break  # Exit if we can't send heartbeat
                continue

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected for session: {session_id[:8]}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for session {session_id[:8]}: {e}")
    finally:
        progress_manager.close_session(session_id)


@app.get("/api/strategy/progress/{session_id}")
async def progress_stream(session_id: str):
    """
    Step 2: Server-Sent Events endpoint for real-time progress updates
    Client opens this BEFORE starting the workflow to ensure no events are missed
    """
    from progress_manager import progress_manager

    async def event_generator() -> AsyncGenerator[str, None]:
        # Get or create session queue
        if session_id in progress_manager.sessions:
            logger.info(f"📡 SSE client connected to existing session: {session_id[:8]}")
            queue = progress_manager.sessions[session_id]
        else:
            logger.info(f"📡 Creating new SSE session: {session_id[:8]}")
            queue = progress_manager.create_session(session_id)

        # Send buffered events first (if any) so late joiners still see them
        if session_id in progress_manager.event_history:
            logger.info(f"📡 Sending {len(progress_manager.event_history[session_id])} buffered events")
            for event in progress_manager.event_history[session_id]:
                yield f"data: {json.dumps(event)}\n\n"

        # Send ready signal
        yield f"data: {json.dumps({'type': 'ready', 'message': 'Stream ready, you can start the workflow'})}\n\n"

        # CRITICAL: Yield control to event loop to ensure the ready signal is sent
        # before we start blocking on queue.get()
        await asyncio.sleep(0)

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


@app.post("/api/sessions/{session_id}/start")
async def start_workflow(
    session_id: str,
    request: StrategyRequest,
    fast_mode: bool = False,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Step 3: Start the workflow AFTER SSE stream is open
    This ensures all events are captured in real-time
    """
    from progress_manager import progress_manager

    logger.info(f"📡 Starting workflow for session {session_id[:8]}")

    # Verify session exists
    if session_id not in progress_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found. Create session first.")

    # Start the actual workflow in background
    asyncio.create_task(_run_multi_agent_workflow(
        session_id=session_id,
        strategy_description=request.strategy_description,
        fast_mode=fast_mode,
        user_id=user_id
    ))

    return {"status": "started", "sessionId": session_id}


@app.post("/api/strategy/create_multi_agent")
async def create_strategy_multi_agent(
    request: StrategyRequest,
    fast_mode: bool = False,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Legacy endpoint: Create and optimize a trading strategy using multi-agent system
    (Kept for backward compatibility, but new clients should use the two-step flow)

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

        # Adjust parameters based on fast mode
        days = 30 if fast_mode else 90  # Ultra-fast mode uses only 30 days
        initial_capital = 10000
        
        result = await supervisor.process({
            'user_query': request.strategy_description,
            'days': days,
            'initial_capital': initial_capital,
            'session_id': session_id,  # Pass session ID for progress updates
            'fast_mode': fast_mode
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

        # Auto-save to chat history after successful strategy creation
        # user_id is guaranteed to exist now since endpoint requires authentication
        try:
            from db.repositories.bot_repository import BotRepository
            from db.models import TradingBotCreate
            bot_repo = BotRepository()

            # Create auto-saved bot entry
            bot_data = TradingBotCreate(
                name=result['strategy'].get('name', 'Untitled Strategy'),
                description=request.strategy_description[:200] if len(request.strategy_description) > 200 else request.strategy_description,
                strategy_config=result['strategy'],
                generated_code=result['code'],
                backtest_results=result['backtest_results'],
                insights_config=result.get('insights_config'),
                session_id=session_id,
                is_saved=False  # Auto-saved, not manually saved
            )

            await bot_repo.create(user_id=user_id, bot_data=bot_data)
            logger.info(f"✅ Auto-saved strategy to chat history for user {user_id}")
        except Exception as save_error:
            logger.error(f"⚠️ Failed to auto-save strategy: {save_error}")
            # Don't fail the request if auto-save fails

        # Store result for later retrieval (in case connection drops)
        if session_id:
            from job_storage import job_storage
            job_storage.store_result(session_id, response_data)

        return response_data

    except Exception as e:
        logger.error(f"❌ Error in multi-agent workflow: {e}")
        import traceback
        traceback.print_exc()
        
        # Store error result so frontend can retrieve it
        if session_id:
            from job_storage import job_storage
            error_data = {
                "success": False,
                "error": str(e),
                "message": "Bot generation failed. Please try again."
            }
            job_storage.store_result(session_id, error_data)
            logger.info(f"📦 Stored error result for session {session_id[:8]}")
        
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


@app.post("/api/strategy/refine")
async def refine_strategy(request: RefineStrategyRequest):
    """
    Refine an existing strategy by modifying the code directly

    This is more efficient than regenerating from scratch because:
    - Only modifies what needs to change
    - Preserves working code and patterns
    - Doesn't waste API credits on regenerating sentiment data
    - Faster iteration cycle

    Args:
        request: Contains current strategy, code, and refinement instructions

    Returns:
        Refined strategy with updated code and backtest results
    """
    try:
        session_id = request.session_id

        logger.info(f"🔧 Refining strategy: {request.refinement_instructions[:100]}")

        # Pre-create progress session
        if session_id:
            from progress_manager import progress_manager
            progress_manager.create_session(session_id)
            progress_manager.update_progress(
                session_id,
                agent="CodeGenerator",
                status="Analyzing refinement request..."
            )

        from agents.code_generator import CodeGeneratorAgent
        from agents.backtest_runner import BacktestRunnerAgent
        from agents.analyst import StrategyAnalystAgent

        # Initialize agents
        code_gen = CodeGeneratorAgent()
        backtest_runner = BacktestRunnerAgent()
        analyst = StrategyAnalystAgent()

        # Step 1: Refine the code
        if session_id:
            progress_manager.update_progress(
                session_id,
                agent="CodeGenerator",
                status="Modifying strategy code..."
            )

        refine_result = await code_gen.refine_existing_code({
            'current_strategy': request.current_strategy,
            'current_code': request.current_code,
            'refinement_instructions': request.refinement_instructions
        })

        if not refine_result.get('success'):
            raise HTTPException(status_code=400, detail="Failed to refine strategy code")

        refined_strategy = refine_result['strategy']
        refined_code = refine_result['code']
        changes_made = refine_result.get('changes_made', [])

        logger.info(f"✅ Code refined. Changes: {', '.join(changes_made)}")

        # Step 2: Run backtest on refined strategy
        if session_id:
            progress_manager.update_progress(
                session_id,
                agent="BacktestRunner",
                status="Running backtest on refined strategy..."
            )

        backtest_result = await backtest_runner.process({
            'strategy': refined_strategy,
            'days': 180,
            'initial_capital': 10000
        })

        if not backtest_result.get('success'):
            raise HTTPException(status_code=400, detail="Backtest failed on refined strategy")

        backtest_results = backtest_result['results']

        # Step 3: Generate insights
        if session_id:
            progress_manager.update_progress(
                session_id,
                agent="StrategyAnalyst",
                status="Generating insights..."
            )

        analysis_result = await analyst.process({
            'strategy': refined_strategy,
            'backtest_results': backtest_results,
            'previous_results': None,
            'iteration': 1
        })

        insights_config = analysis_result.get('insights_config')

        # Mark workflow complete
        if session_id:
            progress_manager.complete_session(session_id)

        response_data = {
            "success": True,
            "session_id": session_id,
            "strategy": refined_strategy,
            "code": refined_code,
            "backtest_results": backtest_results,
            "insights_config": insights_config,
            "changes_made": changes_made,
            "message": f"Strategy refined: {', '.join(changes_made)}"
        }

        # Store result
        if session_id:
            from job_storage import job_storage
            job_storage.store_result(session_id, response_data)

        return response_data

    except Exception as e:
        logger.error(f"❌ Error refining strategy: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(message: dict):
    """
    Chat with the AI about the current trading strategy using Gemini

    Provides context-aware assistance including:
    - Strategy code and parameters
    - Backtest results analysis
    - Suggestions for improvements
    - Answers to specific questions
    """
    try:
        from llm_client import generate_gemini_chat

        user_message = message.get("message", "")
        bot_context = message.get("bot_context", {})

        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Use Gemini with full backtest context
        response_text = generate_gemini_chat(user_message, context=bot_context)

        return {
            "success": True,
            "response": response_text,
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}")
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
    user_id: str = "demo_user"


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
        logger.info(f"🔍 Processing {len(result.items)} shared agents...")
        
        # Use admin client for consistency
        from db.supabase_client import get_supabase_admin
        admin_client = get_supabase_admin()
        
        for i, agent in enumerate(result.items):
            logger.info(f"📋 Processing agent {i+1}: {agent.name}")
            
            # Get original bot data for performance metrics
            original_bot_response = admin_client.table('trading_bots').select('*').eq('id', str(agent.original_bot_id)).execute()
            
            if original_bot_response.data:
                original_bot = original_bot_response.data[0]
                logger.info(f"  ✅ Found original bot: {original_bot.get('name')}")
                
                backtest_results = original_bot.get('backtest_results', {})
                logger.info(f"  📊 Backtest results keys: {list(backtest_results.keys()) if backtest_results else 'None'}")
                
                # Get author name
                author_response = admin_client.table('users').select('full_name').eq('id', str(agent.author_id)).execute()
                author_name = author_response.data[0].get('full_name', 'Anonymous') if author_response.data else 'Anonymous'
                logger.info(f"  👤 Author: {author_name}")
                
                # Get backtest summary
                backtest_summary = backtest_results.get('summary', {}) if backtest_results else {}
                
                agent_data = {
                    "id": str(agent.id),
                    "name": agent.name,
                    "description": agent.description,
                    "author": author_name,
                    "tags": agent.tags,
                    "total_return": backtest_summary.get('total_return', 0.0),
                    "win_rate": backtest_summary.get('win_rate', 0),
                    "total_trades": backtest_summary.get('total_trades', 0),
                    "symbol": original_bot.get('strategy_config', {}).get('asset', 'N/A'),
                    "views": agent.views,
                    "likes": agent.likes,
                    "downloads": agent.downloads,
                    "shared_at": agent.shared_at.isoformat(),
                    "liked": agent.liked
                }
                agents_with_details.append(agent_data)
                logger.info(f"  ✅ Added agent data: {agent_data['name']} by {agent_data['author']}")
            else:
                logger.error(f"  ❌ Original bot not found for agent: {agent.name}")
        
        logger.info(f"🎯 Final agents_with_details count: {len(agents_with_details)}")
        
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
        
        # If database tables don't exist, provide helpful error message
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.error("❌ Database tables not found. Please run the database setup script.")
            raise HTTPException(
                status_code=503, 
                detail="Database tables not found. Please contact administrator to set up community features."
            )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/community/share")
async def share_agent(agent_data: ShareAgentRequest):
    """
    Share an agent with the community
    """
    try:
        from db.models import SharedAgentCreate
        
        logger.info(f"🔍 Share agent request received:")
        logger.info(f"  - agent_id: {agent_data.agent_id}")
        logger.info(f"  - user_id: {agent_data.user_id}")
        logger.info(f"  - name: {agent_data.name}")
        
        # Create shared agent data
        shared_agent_create = SharedAgentCreate(
            original_bot_id=UUID(agent_data.agent_id),
            name=agent_data.name,
            description=agent_data.description,
            tags=agent_data.tags,
            is_public=agent_data.is_public
        )
        
        # Save to database
        # For demo purposes, use a default UUID if user_id is not a valid UUID
        try:
            author_uuid = UUID(agent_data.user_id)
            logger.info(f"✅ Using provided user UUID: {author_uuid}")
        except ValueError:
            # Use a default demo user UUID
            author_uuid = UUID("00000000-0000-0000-0000-000000000001")
            logger.info(f"⚠️ Invalid user_id format, using demo user UUID: {author_uuid}")
        
        # Check if the bot exists and belongs to the user
        from db.supabase_client import get_supabase_admin
        client = get_supabase_admin()
        
        bot_response = client.table('trading_bots').select('*').eq('id', str(shared_agent_create.original_bot_id)).eq('user_id', str(author_uuid)).execute()
        
        if not bot_response.data:
            logger.error(f"❌ Bot not found or not owned by user:")
            logger.error(f"  - Bot ID: {shared_agent_create.original_bot_id}")
            logger.error(f"  - User ID: {author_uuid}")
            
            # Let's see what bots exist for this user
            user_bots = client.table('trading_bots').select('*').eq('user_id', str(author_uuid)).execute()
            logger.error(f"  - User's bots: {len(user_bots.data)} found")
            for bot in user_bots.data[:3]:
                logger.error(f"    - {bot.get('name')} (ID: {bot.get('id')})")
            
            raise Exception("Original bot not found or not owned by user")
        
        logger.info(f"✅ Found bot: {bot_response.data[0].get('name')}")
        
        shared_agent = await community_repo.create_shared_agent(
            author_id=author_uuid,
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
        
        # If database tables don't exist, provide helpful error message
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            logger.error("❌ Database tables not found. Please run the database setup script.")
            raise HTTPException(
                status_code=503, 
                detail="Database tables not found. Please contact administrator to set up community features."
            )
        
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
async def create_bot(bot_data: dict):
    """
    Save an agent to user's bot collection (for Save to My Bots functionality)
    """
    try:
        # For mock purposes, just return success
        # In a real implementation, this would save to the trading_bots table
        user_id = bot_data.get('user_id', 'demo_user')
        logger.info(f"🤖 Bot saved to user collection: {bot_data.get('name', 'Unknown')} for user: {user_id}")
        
        return {
            "success": True,
            "message": "Bot saved to your collection successfully",
            "bot_id": f"user-bot-{uuid.uuid4().hex[:8]}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dev/create-default-user")
async def create_default_user():
    """
    Development endpoint to create the default user for testing
    """
    try:
        from db.supabase_client import get_supabase_admin
        from uuid import UUID

        admin_client = get_supabase_admin()
        default_user_id = "00000000-0000-0000-0000-000000000001"

        # Try to create the default user
        user_data = {
            'id': default_user_id,
            'email': 'dev@mobius.local',
            'full_name': 'Development User',
        }

        response = admin_client.table('users').upsert(user_data, on_conflict='id').execute()

        logger.info(f"✅ Default dev user created/updated: {default_user_id}")
        return {
            "success": True,
            "message": "Default dev user created successfully",
            "user_id": default_user_id
        }
    except Exception as e:
        logger.error(f"❌ Error creating default user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
