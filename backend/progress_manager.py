"""
Progress Event Manager for real-time agent activity updates
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime


class ProgressManager:
    """Manages progress events for real-time updates to clients"""

    def __init__(self):
        self.sessions: Dict[str, asyncio.Queue] = {}
        self.event_history: Dict[str, list] = {}

    def create_session(self, session_id: str) -> asyncio.Queue:
        """Create a new progress tracking session"""
        queue = asyncio.Queue()
        self.sessions[session_id] = queue
        self.event_history[session_id] = []
        return queue

    def close_session(self, session_id: str):
        """Close and cleanup a progress session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def emit_event(self, session_id: str, event: Dict[str, Any]):
        """Emit a progress event to a specific session"""
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"📡 Attempting to emit event to session {session_id[:8] if session_id else 'None'}...")
        logger.info(f"📡 Active sessions: {list(self.sessions.keys())}")

        if session_id in self.sessions:
            event['timestamp'] = datetime.now().isoformat()
            await self.sessions[session_id].put(event)

            # Also store in history for polling
            if session_id not in self.event_history:
                self.event_history[session_id] = []
            self.event_history[session_id].append(event)

            logger.info(f"✅ Event emitted: {event.get('type')} - {event.get('action')}")
        else:
            logger.warning(f"⚠️ Session {session_id[:8] if session_id else 'None'} not in active sessions!")

    async def emit_supervisor_start(self, session_id: str, query: str):
        """Supervisor agent starting"""
        await self.emit_event(session_id, {
            'type': 'agent_start',
            'agent': 'Supervisor',
            'action': 'Reading your request',
            'message': f'Analyzing strategy query...',
            'icon': '🎯'
        })

    async def emit_insights_generation(self, session_id: str):
        """Insights generator analyzing query"""
        await self.emit_event(session_id, {
            'type': 'agent_start',
            'agent': 'InsightsGenerator',
            'action': 'Determining helpful visualizations',
            'message': 'Analyzing what charts would help you understand this strategy...',
            'icon': '🔍'
        })

    async def emit_insights_complete(self, session_id: str, viz_count: int):
        """Insights generation complete"""
        await self.emit_event(session_id, {
            'type': 'agent_complete',
            'agent': 'InsightsGenerator',
            'action': 'Visualizations configured',
            'message': f'Generated {viz_count} custom visualization configs',
            'icon': '✅'
        })

    async def emit_iteration_start(self, session_id: str, iteration: int, max_iterations: int):
        """Starting new iteration"""
        await self.emit_event(session_id, {
            'type': 'iteration_start',
            'iteration': iteration,
            'max_iterations': max_iterations,
            'message': f'Iteration {iteration}/{max_iterations}',
            'icon': '🔄'
        })

    async def emit_code_generation_start(self, session_id: str, iteration: int):
        """Code generator starting"""
        await self.emit_event(session_id, {
            'type': 'agent_start',
            'agent': 'CodeGenerator',
            'action': 'Generating strategy code',
            'message': 'Parsing query and generating trading strategy...',
            'icon': '📝',
            'iteration': iteration
        })

    async def emit_code_generation_complete(self, session_id: str, changes: list):
        """Code generation complete"""
        changes_text = ', '.join(changes[:3]) if changes else 'Initial strategy created'
        await self.emit_event(session_id, {
            'type': 'agent_complete',
            'agent': 'CodeGenerator',
            'action': 'Strategy ready',
            'message': changes_text,
            'icon': '✅'
        })

    async def emit_backtest_start(self, session_id: str, days: int, capital: float):
        """Backtest runner starting"""
        await self.emit_event(session_id, {
            'type': 'agent_start',
            'agent': 'BacktestRunner',
            'action': 'Running backtest',
            'message': f'Testing strategy on {days} days of historical data (${capital:,.0f} capital)...',
            'icon': '📊'
        })

    async def emit_backtest_complete(self, session_id: str, trades: int, return_pct: float):
        """Backtest complete"""
        await self.emit_event(session_id, {
            'type': 'agent_complete',
            'agent': 'BacktestRunner',
            'action': 'Backtest complete',
            'message': f'{trades} trades executed, {return_pct:+.1f}% return',
            'icon': '✅'
        })

    async def emit_analysis_start(self, session_id: str):
        """Strategy analyst starting"""
        await self.emit_event(session_id, {
            'type': 'agent_start',
            'agent': 'StrategyAnalyst',
            'action': 'Analyzing results',
            'message': 'Reviewing backtest performance and checking for issues...',
            'icon': '🔍'
        })

    async def emit_analysis_complete(self, session_id: str, needs_refinement: bool, issues: list):
        """Analysis complete"""
        if needs_refinement:
            issues_text = issues[0] if issues else 'Improvements needed'
            await self.emit_event(session_id, {
                'type': 'agent_complete',
                'agent': 'StrategyAnalyst',
                'action': 'Identified improvements',
                'message': f'Issue found: {issues_text}',
                'icon': '⚠️'
            })
        else:
            await self.emit_event(session_id, {
                'type': 'agent_complete',
                'agent': 'StrategyAnalyst',
                'action': 'Strategy approved',
                'message': 'Results look good! Strategy is ready.',
                'icon': '✅'
            })

    async def emit_refinement(self, session_id: str, suggestion: str):
        """Supervisor deciding to refine"""
        await self.emit_event(session_id, {
            'type': 'refinement',
            'agent': 'Supervisor',
            'action': 'Refining strategy',
            'message': f'Adjusting parameters: {suggestion}',
            'icon': '🔧'
        })

    async def emit_complete(self, session_id: str, iterations: int):
        """Workflow complete"""
        await self.emit_event(session_id, {
            'type': 'complete',
            'agent': 'Supervisor',
            'action': 'Workflow complete',
            'message': f'Strategy optimized through {iterations} iteration(s)',
            'icon': '🎉'
        })

    async def emit_error(self, session_id: str, agent: str, error: str):
        """Error occurred"""
        await self.emit_event(session_id, {
            'type': 'error',
            'agent': agent,
            'action': 'Error occurred',
            'message': error,
            'icon': '❌'
        })


# Global progress manager instance
progress_manager = ProgressManager()
