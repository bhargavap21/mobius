"""
Supervisor Agent - Main orchestrator for multi-agent workflow
"""
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from agents.code_generator import CodeGeneratorAgent
from agents.backtest_runner import BacktestRunnerAgent
from agents.strategy_analyst import StrategyAnalystAgent
from agents.insights_generator import InsightsGeneratorAgent
from agents.intelligent_orchestrator import IntelligentOrchestrator

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Orchestrates the entire workflow

    Workflow:
    1. Receive user strategy request
    2. Generate insights config (what data to visualize)
    3. Send to Code Generator -> get strategy
    4. Send to Backtest Runner -> get results (with insights data)
    5. Send to Strategy Analyst -> get feedback
    6. If needs refinement AND should_continue:
       - Send feedback to Code Generator -> get refined strategy
       - Goto step 4
    7. Return final strategy, code, backtest results, and insights

    Max iterations: 5
    """

    def __init__(self):
        super().__init__("Supervisor")
        self.code_generator = CodeGeneratorAgent()
        self.backtest_runner = BacktestRunnerAgent()
        self.strategy_analyst = StrategyAnalystAgent()
        self.insights_generator = InsightsGeneratorAgent()
        self.max_iterations = 5

        # Initialize intelligent orchestrator for data-driven learning
        self.orchestrator = IntelligentOrchestrator()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration loop

        Args:
            input_data: {
                'user_query': str,
                'days': int (optional),
                'initial_capital': float (optional)
            }

        Returns:
            {
                'success': bool,
                'strategy': dict,
                'code': str,
                'backtest_results': dict,
                'iterations': int,
                'iteration_history': list[dict],
                'final_analysis': dict
            }
        """
        user_query = input_data.get('user_query', '')
        days = input_data.get('days', 180)
        initial_capital = input_data.get('initial_capital', 10000)
        session_id = input_data.get('session_id')  # Optional session ID for progress updates

        # Import progress manager if session_id provided
        progress = None
        if session_id:
            from progress_manager import progress_manager
            progress = progress_manager

        logger.info(f"🎯 Supervisor starting workflow for: '{user_query[:100]}...'")
        logger.info(f"📡 Progress manager: {progress is not None}, Session: {session_id}")
        if progress and session_id:
            logger.info(f"📡 Emitting supervisor start...")
            await progress.emit_supervisor_start(session_id, user_query)
            logger.info(f"✅ Event emitted")

        # STEP -1: Check if this is a politician trading strategy and fetch real data
        politician_data = None
        query_lower = user_query.lower()
        if 'pelosi' in query_lower or 'politician' in query_lower or 'congress' in query_lower or 'senator' in query_lower:
            logger.info(f"🏛️ Detected politician trading request, fetching real data...")
            try:
                from tools.politician_trades import get_politician_trades, get_pelosi_portfolio_tickers

                # Determine which politician
                politician_name = None
                if 'pelosi' in query_lower:
                    politician_name = "Pelosi"

                # Fetch recent trades
                trades_data = get_politician_trades(politician_name=politician_name, days_back=180)
                logger.info(f"✅ Fetched {len(trades_data.get('trades', []))} politician trades")

                # Get portfolio tickers if Pelosi-specific
                if politician_name == "Pelosi":
                    tickers = get_pelosi_portfolio_tickers()
                    logger.info(f"✅ Fetched {len(tickers)} Pelosi portfolio tickers: {tickers[:5]}")
                    politician_data = {
                        'trades': trades_data.get('trades', []),
                        'tickers': tickers,
                        'summary': trades_data.get('summary', {})
                    }
                else:
                    politician_data = {
                        'trades': trades_data.get('trades', []),
                        'summary': trades_data.get('summary', {})
                    }
            except Exception as e:
                logger.error(f"❌ Error fetching politician data: {e}")
                politician_data = None

        # STEP 0: Generate insights configuration (only once at start)
        logger.info(f"🔍 Analyzing query to determine helpful visualizations...")
        if progress:
            await progress.emit_insights_generation(session_id)

        insights_config = None

        iteration_history = []
        strategy = None
        code = None
        backtest_results = None
        feedback = None

        # Track start time to prevent infinite loops
        import time
        start_time = time.time()
        max_workflow_time = 600  # 10 minutes max

        for iteration in range(1, self.max_iterations + 1):
            # Safety check: prevent infinite loops
            if time.time() - start_time > max_workflow_time:
                logger.error(f"⚠️ Workflow exceeded maximum time ({max_workflow_time}s), stopping")
                break
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 ITERATION {iteration}/{self.max_iterations}")
            logger.info(f"{'='*60}\n")

            if progress:
                await progress.emit_iteration_start(session_id, iteration, self.max_iterations)

            iteration_data = {
                'iteration': iteration,
                'steps': []
            }

            # STEP 1: Code Generation
            logger.info(f"📝 Step 1: Code Generation")
            if progress:
                await progress.emit_code_generation_start(session_id, iteration)

            # Pass data insights to code generator if available
            code_input = {
                'user_query': user_query,
                'feedback': feedback,
                'previous_strategy': strategy,
                'iteration': iteration
            }

            # Pass politician trading data if available
            if politician_data:
                code_input['politician_data'] = politician_data
                logger.info(f"🏛️ Passing {len(politician_data.get('trades', []))} politician trades to CodeGenerator...")

            # If we have data insights from previous iteration, include them
            if iteration > 1 and 'data_insights' in locals() and data_insights:
                code_input['data_insights'] = data_insights
                logger.info(f"📊 Passing data insights to CodeGenerator...")

            code_result = await self.code_generator.process(code_input)

            if not code_result.get('success'):
                logger.error(f"❌ Code generation failed: {code_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Code generation failed at iteration {iteration}: {code_result.get('error')}"
                }

            strategy = code_result.get('strategy')
            code = code_result.get('code')
            changes_made = code_result.get('changes_made', [])

            # Generate insights config on first iteration after we have the strategy
            if iteration == 1 and strategy and not insights_config:
                try:
                    logger.info("Generating insights configuration...")
                    # Add timeout to prevent hanging
                    import asyncio
                    insights_config = await asyncio.wait_for(
                        self.insights_generator.analyze_query_for_insights(user_query, strategy),
                        timeout=30.0  # 30 second timeout
                    )
                    logger.info(f"✅ Generated {len(insights_config.get('visualizations', []))} visualization configs")
                    if progress:
                        await progress.emit_insights_complete(session_id, len(insights_config.get('visualizations', [])))
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Insights generation timed out after 30s, continuing without insights")
                    insights_config = {"visualizations": [], "insights": []}
                except Exception as e:
                    logger.error(f"❌ Error generating insights: {e}")
                    insights_config = {"visualizations": [], "insights": []}

            if progress:
                await progress.emit_code_generation_complete(session_id, changes_made)

            iteration_data['steps'].append({
                'agent': 'CodeGenerator',
                'changes_made': changes_made,
                'strategy': strategy
            })

            logger.info(f"✅ Strategy generated/refined")
            if changes_made:
                for change in changes_made:
                    logger.info(f"   - {change}")

            # STEP 2: Backtest
            logger.info(f"\n📊 Step 2: Running Backtest")
            if progress:
                await progress.emit_backtest_start(session_id, days, initial_capital)

            backtest_result = await self.backtest_runner.process({
                'strategy': strategy,
                'feedback': feedback,
                'iteration': iteration,
                'days': days,
                'initial_capital': initial_capital,
                'insights_config': insights_config  # Pass insights config to backtester
            })

            if not backtest_result.get('success'):
                logger.error(f"❌ Backtest failed: {backtest_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Backtest failed at iteration {iteration}: {backtest_result.get('error')}"
                }

            backtest_results = backtest_result.get('results')
            days_used = backtest_result.get('days_used', days)
            warnings = backtest_result.get('warnings', [])

            # Update days for next iteration if changed
            days = days_used

            summary = backtest_results.get('summary', {})
            iteration_data['steps'].append({
                'agent': 'BacktestRunner',
                'days_used': days_used,
                'warnings': warnings,
                'results': summary
            })

            logger.info(f"✅ Backtest complete:")
            logger.info(f"   - Trades: {summary.get('total_trades', 0)}")
            logger.info(f"   - Win Rate: {summary.get('win_rate', 0)}%")
            logger.info(f"   - Return: {summary.get('total_return', 0)}%")
            logger.info(f"   - Days: {days_used}")

            # Intelligent data analysis when we have zero or few trades
            data_insights = None
            if summary.get('total_trades', 0) < 10:
                logger.info(f"🧠 Running intelligent data analysis (trades < 10)...")
                try:
                    data_insights = self.orchestrator.analyze_backtest_data(
                        backtest_results=backtest_results,
                        strategy=strategy
                    )

                    if data_insights and data_insights.get('recommendations'):
                        logger.info(f"📊 Data insights: {data_insights.get('primary_issue')}")
                        for rec in data_insights.get('recommendations', [])[:3]:
                            logger.info(f"   - {rec['condition']}: adjust to {rec['recommended_value']:.3f} "
                                      f"(confidence: {rec['confidence']:.2f})")
                except Exception as e:
                    logger.warning(f"⚠️  Data analysis failed: {e}")

            if progress:
                await progress.emit_backtest_complete(
                    session_id,
                    summary.get('total_trades', 0),
                    summary.get('total_return', 0)
                )

            # STEP 3: Analysis
            logger.info(f"\n🔍 Step 3: Strategy Analysis")
            if progress:
                await progress.emit_analysis_start(session_id)

            analysis_result = await self.strategy_analyst.process({
                'backtest_results': backtest_results,
                'strategy': strategy,
                'user_query': user_query,
                'iteration': iteration
            })

            if not analysis_result.get('success'):
                logger.error(f"❌ Analysis failed: {analysis_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Analysis failed at iteration {iteration}: {analysis_result.get('error')}"
                }

            feedback = analysis_result
            iteration_data['steps'].append({
                'agent': 'StrategyAnalyst',
                'analysis': analysis_result.get('analysis'),
                'issues': analysis_result.get('issues', []),
                'suggestions': analysis_result.get('suggestions', []),
                'needs_refinement': analysis_result.get('needs_refinement'),
                'should_continue': analysis_result.get('should_continue')
            })

            logger.info(f"✅ Analysis complete:")
            logger.info(f"   - Analysis: {analysis_result.get('analysis', 'N/A')[:100]}...")
            logger.info(f"   - Issues: {len(analysis_result.get('issues', []))}")
            logger.info(f"   - Suggestions: {len(analysis_result.get('suggestions', []))}")

            if progress:
                await progress.emit_analysis_complete(
                    session_id,
                    analysis_result.get('needs_refinement', False),
                    analysis_result.get('issues', [])
                )
            logger.info(f"   - Needs Refinement: {analysis_result.get('needs_refinement')}")
            logger.info(f"   - Should Continue: {analysis_result.get('should_continue')}")

            iteration_history.append(iteration_data)

            # DECISION: Should we continue iterating?
            needs_refinement = analysis_result.get('needs_refinement', False)
            should_continue = analysis_result.get('should_continue', True)

            if not needs_refinement:
                logger.info(f"\n✅ Strategy is satisfactory! Stopping iterations.")
                break

            if not should_continue:
                logger.info(f"\n⚠️  Analyst recommends stopping iterations.")
                break

            if iteration >= self.max_iterations:
                logger.info(f"\n⚠️  Reached max iterations ({self.max_iterations})")
                break

            logger.info(f"\n🔄 Strategy needs refinement. Continuing to next iteration...")
            if progress and analysis_result.get('suggestions'):
                suggestion_text = analysis_result.get('suggestions', [])[0] if analysis_result.get('suggestions') else 'Refining strategy'
                await progress.emit_refinement(session_id, suggestion_text)

        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 WORKFLOW COMPLETE - {iteration} iterations")
        logger.info(f"{'='*60}\n")

        if progress:
            await progress.emit_complete(session_id, iteration)

        final_summary = backtest_results.get('summary', {})
        logger.info(f"📊 Final Results:")
        logger.info(f"   - Asset: {strategy.get('asset', 'N/A')}")
        logger.info(f"   - Total Trades: {final_summary.get('total_trades', 0)}")
        logger.info(f"   - Win Rate: {final_summary.get('win_rate', 0)}%")
        logger.info(f"   - Total Return: {final_summary.get('total_return', 0)}%")
        logger.info(f"   - Buy & Hold: {final_summary.get('buy_hold_return', 0)}%")
        logger.info(f"   - Sharpe Ratio: {final_summary.get('sharpe_ratio', 0)}")

        return {
            'success': True,
            'strategy': strategy,
            'code': code,
            'backtest_results': backtest_results,
            'iterations': iteration,
            'iteration_history': iteration_history,
            'final_analysis': feedback,
            'insights_config': insights_config  # Include insights configuration
        }

    def get_workflow_summary(self, iteration_history: List[Dict[str, Any]]) -> str:
        """Generate a human-readable summary of the workflow"""
        summary = []
        summary.append("## Multi-Agent Workflow Summary\n")

        for i, iteration_data in enumerate(iteration_history, 1):
            summary.append(f"### Iteration {i}")

            for step in iteration_data.get('steps', []):
                agent = step.get('agent')
                summary.append(f"\n**{agent}:**")

                if agent == 'CodeGenerator':
                    changes = step.get('changes_made', [])
                    if changes:
                        for change in changes:
                            summary.append(f"  - {change}")
                    else:
                        summary.append(f"  - Initial strategy generated")

                elif agent == 'BacktestRunner':
                    results = step.get('results', {})
                    summary.append(f"  - Trades: {results.get('total_trades', 0)}")
                    summary.append(f"  - Return: {results.get('total_return', 0):.2f}%")
                    summary.append(f"  - Win Rate: {results.get('win_rate', 0):.1f}%")

                elif agent == 'StrategyAnalyst':
                    issues = step.get('issues', [])
                    suggestions = step.get('suggestions', [])
                    if issues:
                        summary.append(f"  - Issues: {len(issues)}")
                    if suggestions:
                        summary.append(f"  - Suggestions: {len(suggestions)}")

            summary.append("")

        return "\n".join(summary)
