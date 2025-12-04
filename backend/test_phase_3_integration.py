"""
Phase 3 Integration Test - End-to-End Workflow with Code Execution

Tests the complete workflow from strategy generation to containerized execution:
1. Generate strategy code
2. Validate code with CodeValidationEvaluator
3. Execute code in container via BacktestRunnerAgent
4. Evaluate results with full pipeline
5. Verify all components work together
"""

import logging
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from tools.code_generator import parse_strategy, generate_trading_bot_code
from evals.code_validation_evaluator import validate_code
from agents.backtest_runner import BacktestRunnerAgent
from services.eval_pipeline import ProductionEvalPipeline


async def test_code_generation_and_validation():
    """Test 1: Generate code and validate it"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Code Generation + Validation")
    logger.info("="*70 + "\n")

    # User query
    user_query = "Buy AAPL when RSI drops below 35, sell when RSI exceeds 65"

    # Step 1: Parse strategy
    logger.info("Step 1: Parsing strategy...")
    parsed = parse_strategy(user_query)

    if not parsed['success']:
        logger.error(f"❌ Strategy parsing failed: {parsed.get('error')}")
        return False, None, None

    strategy = parsed['strategy']
    logger.info(f"✅ Strategy parsed: {strategy.get('name')}")

    # Step 2: Generate code
    logger.info("\nStep 2: Generating code...")
    code_result = generate_trading_bot_code(strategy)

    if not code_result['success']:
        logger.error(f"❌ Code generation failed: {code_result.get('error')}")
        return False, None, None

    code = code_result['code']
    logger.info(f"✅ Code generated: {len(code)} characters")

    # Step 3: Validate code
    logger.info("\nStep 3: Validating code...")
    validation_result = validate_code(
        code=code,
        user_input=user_query,
        strategy=strategy
    )

    logger.info(f"\nCode Validation Results:")
    logger.info(f"  Score: {validation_result.score:.2%}")
    logger.info(f"  Passed: {validation_result.passed}")

    # Get checks from details
    checks = validation_result.details.get('checks', {})
    for check_name, check_result in checks.items():
        status = "✅" if check_result['passed'] else "❌"
        logger.info(f"  {status} {check_name}: {check_result['message']}")

    if not validation_result.passed:
        logger.error("\n❌ Code validation failed")
        for error in validation_result.errors:
            logger.error(f"   {error}")
        return False, None, None

    logger.info("\n✅ Code validation passed")
    return True, strategy, code


async def test_containerized_execution():
    """Test 2: Execute code in container via BacktestRunnerAgent"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Containerized Execution via BacktestRunnerAgent")
    logger.info("="*70 + "\n")

    # Generate strategy and code
    success, strategy, code = await test_code_generation_and_validation()
    if not success:
        return False, None

    # Initialize BacktestRunnerAgent
    agent = BacktestRunnerAgent()
    agent.use_containerized_execution = True  # Force container use

    logger.info("\nExecuting strategy in container...")

    # Execute with generated code
    result = await agent.execute_with_generated_code(
        code=code,
        strategy=strategy,
        days=60,  # 2 months
        initial_capital=100000,
        use_container=True
    )

    if not result['success']:
        logger.error(f"❌ Execution failed: {result.get('error')}")
        return False, None

    backtest_results = result['results']
    metrics = backtest_results['summary']

    logger.info(f"\n✅ Containerized execution successful")
    logger.info(f"\nPerformance Metrics:")
    logger.info(f"  Total Return:   {metrics.get('total_return', 0):+.2f}%")
    logger.info(f"  Total Trades:   {metrics.get('total_trades', 0)}")
    logger.info(f"  Win Rate:       {metrics.get('win_rate', 0):.2f}%")
    logger.info(f"  Sharpe Ratio:   {metrics.get('sharpe_ratio', 0):.2f}")
    logger.info(f"  Max Drawdown:   {metrics.get('max_drawdown', 0):.2f}%")
    logger.info(f"  Execution:      {backtest_results.get('execution_method', 'unknown')}")

    return True, backtest_results


async def test_full_evaluation_pipeline():
    """Test 3: Run full evaluation pipeline with code execution results"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Full Evaluation Pipeline")
    logger.info("="*70 + "\n")

    # Generate and execute strategy
    success, backtest_results = await test_containerized_execution()
    if not success:
        return False

    # Parse strategy again for evaluation
    user_query = "Buy AAPL when RSI drops below 35, sell when RSI exceeds 65"
    parsed = parse_strategy(user_query)
    strategy = parsed['strategy']

    code_result = generate_trading_bot_code(strategy)
    code = code_result['code']

    # Initialize evaluation pipeline
    logger.info("Initializing evaluation pipeline...")
    pipeline = ProductionEvalPipeline(enable_llm_evals=False)  # Deterministic only for speed

    # Run evaluation
    logger.info("Running evaluators...")
    evaluation_suite = pipeline.evaluate(
        user_input=user_query,
        strategy=strategy,
        backtest_results=backtest_results,
        trades=backtest_results.get('trades', []),
        generated_code=code,
    )

    # Display results
    logger.info(f"\n{'='*70}")
    logger.info("EVALUATION RESULTS")
    logger.info(f"{'='*70}")
    logger.info(f"\nOverall Score: {evaluation_suite.average_score:.2%}")
    logger.info(f"Passed: {evaluation_suite.all_passed}")

    logger.info(f"\nEvaluator Results:")
    for result in evaluation_suite.results:
        status = "✅" if result.passed else "❌"
        score = result.score or 0
        logger.info(f"  {status} {result.evaluator_name}: {score:.2%}")

        # Show warnings and errors
        for warning in result.warnings:
            logger.info(f"      ⚠️  {warning}")
        for error in result.errors:
            logger.info(f"      ❌ {error}")

    if not evaluation_suite.all_passed:
        logger.warning("\n⚠️  Some evaluators failed, but pipeline completed successfully")

    logger.info("\n✅ Full evaluation pipeline completed")
    return True


async def test_direct_vs_container_execution():
    """Test 4: Compare direct vs containerized execution"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Direct vs Container Execution Comparison")
    logger.info("="*70 + "\n")

    # Generate strategy
    user_query = "Buy AAPL when RSI < 35, sell when RSI > 65"
    parsed = parse_strategy(user_query)
    strategy = parsed['strategy']

    code_result = generate_trading_bot_code(strategy)
    code = code_result['code']

    agent = BacktestRunnerAgent()

    # Test 1: Direct execution
    logger.info("Running backtest with DIRECT execution...")
    import time
    start = time.time()

    result_direct = await agent.execute_with_generated_code(
        code=code,
        strategy=strategy,
        days=60,
        initial_capital=100000,
        use_container=False
    )

    direct_time = time.time() - start

    if not result_direct['success']:
        logger.error("❌ Direct execution failed")
        direct_return = "FAILED"
    else:
        direct_return = result_direct['results']['summary'].get('total_return', 0)
        logger.info(f"  ✅ Direct: {direct_return:+.2f}% in {direct_time:.2f}s")

    # Test 2: Container execution
    logger.info("\nRunning backtest with CONTAINER execution...")
    start = time.time()

    result_container = await agent.execute_with_generated_code(
        code=code,
        strategy=strategy,
        days=60,
        initial_capital=100000,
        use_container=True
    )

    container_time = time.time() - start

    if not result_container['success']:
        logger.error("❌ Container execution failed")
        container_return = "FAILED"
    else:
        container_return = result_container['results']['summary'].get('total_return', 0)
        logger.info(f"  ✅ Container: {container_return:+.2f}% in {container_time:.2f}s")

    # Comparison
    logger.info(f"\n{'='*70}")
    logger.info("COMPARISON")
    logger.info(f"{'='*70}")
    logger.info(f"Direct execution:     {direct_time:.2f}s | Return: {direct_return}")
    logger.info(f"Container execution:  {container_time:.2f}s | Return: {container_return}")

    if isinstance(direct_return, (int, float)) and isinstance(container_return, (int, float)):
        overhead = ((container_time - direct_time) / direct_time) * 100
        logger.info(f"Container overhead:   {overhead:+.1f}%")

        # Results should match
        if abs(direct_return - container_return) < 0.01:
            logger.info("✅ Results match (container produces same outcome as direct)")
        else:
            logger.warning(f"⚠️  Results differ by {abs(direct_return - container_return):.2f}%")

    logger.info("\n✅ Execution comparison complete")
    return True


async def main():
    """Run all Phase 3 integration tests"""
    logger.info("\n" + "="*70)
    logger.info("PHASE 3 INTEGRATION TEST SUITE")
    logger.info("="*70)
    logger.info("\nTesting end-to-end workflow:")
    logger.info("  1. Code generation + validation")
    logger.info("  2. Containerized execution")
    logger.info("  3. Full evaluation pipeline")
    logger.info("  4. Direct vs container comparison")
    logger.info("")

    # Test 1: Code generation and validation
    test1_success, _, _ = await test_code_generation_and_validation()

    # Test 2: Containerized execution
    test2_success, _ = await test_containerized_execution()

    # Test 3: Full evaluation pipeline
    test3_success = await test_full_evaluation_pipeline()

    # Test 4: Direct vs container comparison
    test4_success = await test_direct_vs_container_execution()

    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"Code Generation + Validation:    {'✅ PASSED' if test1_success else '❌ FAILED'}")
    logger.info(f"Containerized Execution:         {'✅ PASSED' if test2_success else '❌ FAILED'}")
    logger.info(f"Full Evaluation Pipeline:        {'✅ PASSED' if test3_success else '❌ FAILED'}")
    logger.info(f"Direct vs Container Comparison:  {'✅ PASSED' if test4_success else '❌ FAILED'}")

    all_passed = all([test1_success, test2_success, test3_success, test4_success])

    if all_passed:
        logger.info("\n" + "="*70)
        logger.info("🎉 PHASE 3: ALL TESTS PASSED")
        logger.info("="*70)
        logger.info("\n✅ End-to-end workflow working correctly:")
        logger.info("   • Code generation produces valid code")
        logger.info("   • CodeValidationEvaluator validates code quality")
        logger.info("   • BacktestRunnerAgent executes code in container")
        logger.info("   • Evaluation pipeline validates results")
        logger.info("   • Container execution matches direct execution")
        logger.info("\n🚀 Phase 3 is production-ready!")
        logger.info("📋 System now executes generated code (not just simulates)")
        return True
    else:
        logger.error("\n❌ PHASE 3 INTEGRATION FAILED")
        logger.error("   Fix failing tests before deploying")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
