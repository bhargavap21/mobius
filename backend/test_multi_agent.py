#!/usr/bin/env python3
"""
Test script for multi-agent orchestration system
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.supervisor import SupervisorAgent


async def test_multi_agent():
    """Test the multi-agent system with a challenging strategy"""

    print("\n" + "=" * 80)
    print("🤖 MULTI-AGENT ORCHESTRATION SYSTEM TEST")
    print("=" * 80 + "\n")

    # Test case: RSI strategy that will likely have issues
    test_query = """
    Buy AAPL when RSI drops below 30.
    Sell when RSI goes above 70 or at -1% stop loss.
    """

    print(f"📝 Test Strategy:")
    print(f"   {test_query.strip()}\n")

    supervisor = SupervisorAgent()

    result = await supervisor.process({
        'user_query': test_query,
        'days': 180,
        'initial_capital': 10000
    })

    if result.get('success'):
        print("\n" + "=" * 80)
        print("✅ MULTI-AGENT WORKFLOW SUCCEEDED")
        print("=" * 80 + "\n")

        print(f"📊 Final Results:")
        print(f"   - Iterations: {result['iterations']}")
        print(f"   - Asset: {result['strategy'].get('asset', 'N/A')}")

        final_summary = result['backtest_results'].get('summary', {})
        print(f"   - Total Trades: {final_summary.get('total_trades', 0)}")
        print(f"   - Win Rate: {final_summary.get('win_rate', 0)}%")
        print(f"   - Total Return: {final_summary.get('total_return', 0)}%")
        print(f"   - Buy & Hold: {final_summary.get('buy_hold_return', 0)}%")

        print(f"\n📋 Iteration History:")
        for i, iteration in enumerate(result['iteration_history'], 1):
            print(f"\n   Iteration {i}:")
            for step in iteration['steps']:
                agent = step['agent']
                if agent == 'CodeGenerator':
                    changes = step.get('changes_made', [])
                    if changes:
                        print(f"      - CodeGenerator: {', '.join(changes[:2])}")
                    else:
                        print(f"      - CodeGenerator: Initial strategy")
                elif agent == 'BacktestRunner':
                    results = step.get('results', {})
                    print(f"      - BacktestRunner: {results.get('total_trades', 0)} trades, {results.get('total_return', 0):.2f}% return")
                elif agent == 'StrategyAnalyst':
                    issues_count = len(step.get('issues', []))
                    suggestions_count = len(step.get('suggestions', []))
                    needs_refinement = step.get('needs_refinement', False)
                    print(f"      - StrategyAnalyst: {issues_count} issues, {suggestions_count} suggestions, Needs Refinement: {needs_refinement}")

        print(f"\n🎯 Final Analysis:")
        final_analysis = result.get('final_analysis', {})
        print(f"   {final_analysis.get('analysis', 'N/A')}")

        if final_analysis.get('issues'):
            print(f"\n   Issues:")
            for issue in final_analysis['issues'][:3]:
                print(f"      - {issue}")

        if final_analysis.get('suggestions'):
            print(f"\n   Suggestions:")
            for suggestion in final_analysis['suggestions'][:3]:
                print(f"      - {suggestion}")

        print("\n" + "=" * 80)

    else:
        print(f"\n❌ WORKFLOW FAILED: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_multi_agent())
