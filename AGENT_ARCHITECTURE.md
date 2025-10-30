# Agent Orchestration Architecture

## Overview

The system uses a **custom-built multi-agent architecture** with **direct API calls to Anthropic Claude and Google Gemini** - **NO frameworks like LangChain or LangGraph**.

## Architecture Type: Custom Multi-Agent System

### Why Custom Built?
- **Full control** over agent communication and workflow
- **Lightweight** - no framework overhead
- **Flexible** - easy to modify agent behavior and add new agents
- **Real-time progress tracking** - custom WebSocket event system
- **Async/await native** - built on Python's asyncio for true concurrency

## Agent Hierarchy

```
┌─────────────────────────────────────────────────────┐
│           SupervisorAgent (Orchestrator)            │
│  - Manages workflow & iteration loop               │
│  - Coordinates all agents                          │
│  - Emits real-time progress events                 │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌──────────────┐  ┌──────────────────────┐
│ Phase 1:     │  │ IntelligentOrchestrator│
│ Analyze      │  │ - Data-driven insights │
└──────┬───────┘  │ - Learning system      │
       │          └──────────────────────────┘
       │
   ┌───┴────┬──────────┬─────────────┐
   ▼        ▼          ▼             ▼
┌──────┐ ┌─────┐ ┌──────────┐ ┌─────────┐
│Insights│Code │ │Backtest  │ │Strategy │
│Gen    │Gen  │ │Runner    │ │Analyst  │
└──────┘ └─────┘ └──────────┘ └─────────┘
```

## Core Components

### 1. **Base Agent** ([base_agent.py](backend/agents/base_agent.py))
```python
class BaseAgent(ABC):
    """Abstract base class for all agents"""
    - name: str
    - memory: list[Dict]  # Agent memory/history

    @abstractmethod
    async def process(input_data) -> output_data
```

**Key Features:**
- Memory system for context retention
- Abstract `process()` method all agents implement
- No external framework dependencies

### 2. **Supervisor Agent** ([supervisor.py](backend/agents/supervisor.py))
```python
class SupervisorAgent(BaseAgent):
    """Main orchestrator - manages the entire workflow"""

    Workflow:
    1. Receive user strategy request
    2. Generate insights config (InsightsGenerator)
    3. ITERATION LOOP (max 2-5 iterations):
       a. Generate/refine code (CodeGenerator)
       b. Run backtest (BacktestRunner)
       c. Analyze results (StrategyAnalyst)
       d. If needs refinement -> continue loop
    4. Return final strategy + results
```

**Orchestration Pattern:**
```python
async def process(input_data):
    # Phase 1: Initial setup
    insights_config = await insights_generator.process(...)

    # Phase 2: Iteration loop
    for iteration in range(1, max_iterations + 1):
        # Step 1: Code generation
        code_result = await code_generator.process(...)

        # Step 2: Backtesting
        backtest_result = await backtest_runner.process(...)

        # Step 3: Analysis
        analysis = await strategy_analyst.process(...)

        # Step 4: Check if refinement needed
        if not analysis['needs_refinement']:
            break

    return final_result
```

### 3. **Individual Agents**

#### CodeGeneratorAgent ([code_generator.py](backend/agents/code_generator.py))
- **Purpose**: Parse strategy description → Generate trading bot code
- **LLM Calls**: Direct Anthropic API calls via `llm_client.generate_text()`
- **Intelligence**:
  - Initial strategy parsing
  - Parameter refinement based on feedback
  - Data-driven adjustments from IntelligentOrchestrator

#### BacktestRunnerAgent ([backtest_runner.py](backend/agents/backtest_runner.py))
- **Purpose**: Execute backtest on generated strategy
- **No LLM**: Pure Python execution using Backtrader library
- **Output**: Performance metrics, trade history, P&L

#### StrategyAnalystAgent ([strategy_analyst.py](backend/agents/strategy_analyst.py))
- **Purpose**: Analyze backtest results → Provide improvement suggestions
- **LLM Calls**: Direct Anthropic API calls
- **Intelligence**: Identifies issues, suggests parameter adjustments

#### InsightsGeneratorAgent ([insights_generator.py](backend/agents/insights_generator.py))
- **Purpose**: Determine what charts/visualizations would be helpful
- **LLM Calls**: Direct Anthropic API calls
- **Output**: Custom visualization configs for frontend

### 4. **IntelligentOrchestrator** ([intelligent_orchestrator.py](backend/agents/intelligent_orchestrator.py))
- **Purpose**: Data-driven learning system
- **Intelligence**: Analyzes actual market data to suggest parameter adjustments
- **Example**: If RSI never hits threshold, automatically suggest relaxing it

## LLM Communication Layer

### Direct API Calls (No Framework)

**LLM Client** ([llm_client.py](backend/llm_client.py)):
```python
# Simple wrapper around Anthropic SDK
def generate_text(prompt, system_instruction, max_tokens):
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        system=system_instruction
    )
    return response.content[0].text

def generate_json(prompt, system_instruction):
    # Same as above but parses JSON from response
    ...
```

**Supported Models:**
- **Primary**: Anthropic Claude 3.5 Sonnet (via `anthropic` SDK)
- **Secondary**: Google Gemini (via `google-generativeai` SDK)
- **No OpenAI** in production (only imported, not actively used)

### Why Direct API Calls vs LangChain?

**Advantages:**
1. ✅ **Full control** over prompts and responses
2. ✅ **No abstraction overhead** - simpler debugging
3. ✅ **Lighter dependencies** - fewer breaking changes
4. ✅ **Custom event system** - real-time WebSocket progress
5. ✅ **Async native** - built on asyncio, not bolted on

**Trade-offs:**
1. ❌ No built-in memory management (custom implementation)
2. ❌ No pre-built chains (custom workflow in Supervisor)
3. ❌ No automatic retries (manual error handling)

## Real-Time Progress System

### Custom WebSocket Event System
```python
# progress_manager.py
class ProgressManager:
    sessions: Dict[session_id, asyncio.Queue]

    async def emit_event(session_id, event):
        await queue.put(event)
        await asyncio.sleep(0)  # Yield to event loop
```

**Event Flow:**
```
Agent executes
    ↓
Calls progress.emit_event()
    ↓
Event added to asyncio.Queue
    ↓
WebSocket listener retrieves from queue
    ↓
Sent to frontend in real-time
```

**Event Types:**
- `agent_start` - Agent begins processing
- `agent_complete` - Agent finishes
- `iteration_start` - New iteration begins
- `refinement` - Strategy refinement happening
- `complete` - Workflow complete
- `error` - Error occurred
- `heartbeat` - Keep-alive ping

## Workflow Example

```
User: "Buy AAPL when RSI < 30, sell when RSI > 70"
    ↓
1. SupervisorAgent receives request
    ↓
2. InsightsGenerator → "Show RSI chart, P&L over time"
    ↓
3. ITERATION 1:
   - CodeGenerator → Parses strategy, generates code
   - BacktestRunner → Runs backtest, 0 trades
   - StrategyAnalyst → "RSI never hit 30, too strict"
   - IntelligentOrchestrator → "Actual RSI min: 35, suggest 35"
    ↓
4. ITERATION 2:
   - CodeGenerator → Adjusts RSI threshold to 35
   - BacktestRunner → Runs backtest, 5 trades, +12% return
   - StrategyAnalyst → "Good! Sufficient trades"
    ↓
5. Return final strategy + code + results
```

## Key Design Decisions

### 1. **Async/Await Native**
- All agents use `async def process()`
- True concurrency with asyncio
- Non-blocking I/O for LLM calls and backtests

### 2. **Stateless Agents**
- Agents don't maintain state between calls
- State passed via `input_data` and `output_data`
- Enables easy scaling and parallelization

### 3. **Event-Driven Progress**
- Custom WebSocket system for real-time updates
- No polling - push-based architecture
- 30-second timeout with heartbeat keep-alive

### 4. **Iterative Refinement**
- Built-in iteration loop (2-5 iterations)
- Each iteration refines based on previous results
- Data-driven adjustments from IntelligentOrchestrator

## Dependencies

**Core:**
- `anthropic>=0.39.0` - Claude API client
- `google-generativeai` - Gemini API client (secondary)
- `fastapi` - Web framework
- `websockets` - Real-time communication

**NO:**
- ❌ LangChain
- ❌ LangGraph
- ❌ AutoGen
- ❌ CrewAI
- ❌ Any agent framework

## Future Enhancements (Potential)

If needed, could add:
1. **Agent parallelization** - Run multiple backtests concurrently
2. **Memory persistence** - Save agent learning across sessions
3. **Tool use** - Give agents access to external tools (APIs, databases)
4. **Multi-model support** - Route different tasks to different models
5. **Caching** - Cache LLM responses for repeated queries

## Summary

**Architecture**: Custom multi-agent system with direct API calls
**Framework**: None - built from scratch
**LLM Provider**: Anthropic Claude (primary), Google Gemini (secondary)
**Orchestration**: SupervisorAgent with iterative refinement loop
**Communication**: Async/await with custom WebSocket progress system
**Design Philosophy**: Simplicity, control, and real-time feedback
