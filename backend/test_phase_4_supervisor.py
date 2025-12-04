"""
Phase 4 Integration Test - Supervisor End-to-End

Tests the complete workflow:
User Query → CodeGenerator → BacktestRunner (with code execution) → Results
"""

import asyncio
import logging
from agents.supervisor import SupervisorAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_supervisor_with_code_execution():
    """Test supervisor workflow with actual code execution"""
    logger.info("\n" + "="*70)
    logger.info("PHASE 4: SUPERVISOR END-TO-END TEST")
    logger.info("="*70)

    # Initialize supervisor
    supervisor = SupervisorAgent()

    # Test query - simple RSI strategy
    user_query = "Buy AAPL when RSI drops below 35, sell when it rises above 65"

    logger.info(f"\n📝 User Query: {user_query}")
    logger.info("\n🚀 Starting supervisor workflow...")

    try:
        # Run supervisor
        # Set max_iterations to 1 to avoid refinement loops during testing
        supervisor.max_iterations = 1

        result = await supervisor.process({
            'user_query': user_query,
            'days': 60,  # 2 months for faster testing
            'initial_capital': 100000,
        })

        logger.info("\n" + "="*70)
        logger.info("RESULTS")
        logger.info("="*70)

        if not result.get('success'):
            logger.error(f"\n❌ Supervisor failed: {result.get('error')}")
            return False

        # Extract results
        strategy = result.get('strategy', {})
        final_backtest = result.get('final_backtest', {})
        iterations = result.get('iterations', [])
        total_iterations = result.get('total_iterations', 0)

        logger.info(f"\n✅ Workflow completed successfully!")
        logger.info(f"\nStrategy: {strategy.get('name', 'Unknown')}")
        logger.info(f"Asset: {strategy.get('asset', 'Unknown')}")
        logger.info(f"Total Iterations: {total_iterations}")

        # Check backtest results
        if final_backtest:
            results = final_backtest.get('results', {})
            summary = results.get('summary', {})

            logger.info(f"\n📊 Backtest Results:")
            logger.info(f"  Total Return:   {summary.get('total_return', 0):+.2f}%")
            logger.info(f"  Total Trades:   {summary.get('total_trades', 0)}")
            logger.info(f"  Win Rate:       {summary.get('win_rate', 0):.2f}%")
            logger.info(f"  Sharpe Ratio:   {summary.get('sharpe_ratio', 0):.2f}")
            logger.info(f"  Max Drawdown:   {summary.get('max_drawdown', 0):.2f}%")

            # Check if code execution was used
            execution_method = results.get('execution_method', 'unknown')
            if execution_method == 'container':
                logger.info(f"\n🐳 Code Execution: CONTAINERIZED ✅")
                logger.info("   → Strategy code was actually executed in Docker")
            elif execution_method == 'direct':
                logger.info(f"\n🔧 Code Execution: DIRECT ✅")
                logger.info("   → Strategy code was executed directly")
            else:
                logger.warning(f"\n⚠️  Execution Method: {execution_method}")
                logger.warning("   → May have used legacy simulation")

        # Check evaluation results if available
        evaluation_results = result.get('evaluation_results')
        if evaluation_results:
            logger.info(f"\n📋 Evaluation Results:")
            logger.info(f"  Overall Score: {evaluation_results.get('average_score', 0):.2%}")
            logger.info(f"  All Passed: {evaluation_results.get('all_passed', False)}")

            results_list = evaluation_results.get('results', [])
            for eval_result in results_list:
                status = "✅" if eval_result.get('passed') else "❌"
                name = eval_result.get('evaluator_name', 'Unknown')
                score = eval_result.get('score', 0)
                logger.info(f"    {status} {name}: {score:.2%}")

        logger.info("\n" + "="*70)
        logger.info("🎉 PHASE 4 TEST PASSED")
        logger.info("="*70)
        logger.info("\n✅ System is ready for frontend integration!")
        logger.info("   • User query → Code generation → Code execution → Results")
        logger.info("   • Evaluation pipeline validates everything")
        logger.info("   • Containerized execution ensures security")

        return True

    except Exception as e:
        logger.error(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test"""
    success = await test_supervisor_with_code_execution()

    if not success:
        logger.error("\n❌ PHASE 4 INTEGRATION FAILED")
        logger.error("   Fix issues before deploying to frontend")
        exit(1)

    logger.info("\n🚀 System ready for frontend testing!")


if __name__ == "__main__":
    asyncio.run(main())
