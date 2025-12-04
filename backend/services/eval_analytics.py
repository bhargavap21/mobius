"""
Evaluation Analytics - Track evaluation failures to identify bugs in the system

This module helps developers identify patterns in evaluation failures that indicate
bugs in the code generator, backtester, or other system components.

Usage:
    1. Evaluation results are automatically logged after each workflow
    2. Query the analytics to find patterns (e.g., "TradeExecutionValidator fails 40% of the time")
    3. Use failure details to identify and fix bugs in YOUR system code
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Store analytics in a JSON file (can be upgraded to DB later)
ANALYTICS_DIR = Path(__file__).parent.parent / "data" / "eval_analytics"
ANALYTICS_FILE = ANALYTICS_DIR / "evaluation_history.jsonl"


def ensure_analytics_dir():
    """Create analytics directory if it doesn't exist"""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def log_evaluation_result(
    user_input: str,
    strategy: Dict[str, Any],
    backtest_results: Dict[str, Any],
    evaluation_results: Dict[str, Any],
    session_id: Optional[str] = None,
):
    """
    Log evaluation results for later analysis.

    This creates a record that helps developers identify:
    - Which evaluators fail most often (system bugs)
    - Common failure patterns (template issues)
    - Correlation between strategy types and failures
    """
    ensure_analytics_dir()

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,

        # User request summary (for pattern matching)
        "user_input_summary": user_input[:200] if user_input else "",
        "user_input_keywords": extract_keywords(user_input),

        # Strategy metadata
        "strategy_name": strategy.get("name", "unknown"),
        "strategy_asset": strategy.get("asset", "unknown"),
        "strategy_type": categorize_strategy(strategy),
        "indicators_used": list(strategy.get("indicators", {}).keys()) if strategy else [],

        # Backtest summary
        "total_trades": backtest_results.get("summary", {}).get("total_trades", 0) if backtest_results else 0,
        "win_rate": backtest_results.get("summary", {}).get("win_rate", 0) if backtest_results else 0,
        "total_return": backtest_results.get("summary", {}).get("total_return", 0) if backtest_results else 0,

        # Evaluation results - THE KEY DATA
        "all_passed": evaluation_results.get("all_passed"),
        "average_score": evaluation_results.get("average_score", 0),
        "failed_evaluators": evaluation_results.get("failed_evaluators", []),
        "passed_evaluators": evaluation_results.get("passed_evaluators", []),

        # Detailed errors for debugging
        "errors": evaluation_results.get("errors", []),

        # Individual evaluator scores
        "evaluator_scores": {
            name: result.get("score", 0)
            for name, result in evaluation_results.get("results", {}).items()
        },

        # Individual evaluator details (for deep debugging)
        "evaluator_details": {
            name: {
                "passed": result.get("passed"),
                "score": result.get("score", 0),
                "error": result.get("error"),
            }
            for name, result in evaluation_results.get("results", {}).items()
        },
    }

    # Append to JSONL file
    try:
        with open(ANALYTICS_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"📊 Logged evaluation analytics: passed={record['all_passed']}, failed={record['failed_evaluators']}")
    except Exception as e:
        logger.warning(f"Failed to log evaluation analytics: {e}")


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from user input for pattern matching"""
    if not text:
        return []

    keywords = []
    text_lower = text.lower()

    # Strategy types
    if "rsi" in text_lower:
        keywords.append("rsi")
    if "macd" in text_lower:
        keywords.append("macd")
    if "bollinger" in text_lower:
        keywords.append("bollinger")
    if "moving average" in text_lower or "sma" in text_lower or "ema" in text_lower:
        keywords.append("moving_average")
    if "sentiment" in text_lower:
        keywords.append("sentiment")
    if "reddit" in text_lower or "wsb" in text_lower:
        keywords.append("reddit")

    # Position sizing
    if "partial" in text_lower:
        keywords.append("partial_position")
    if "50%" in text_lower or "half" in text_lower:
        keywords.append("half_position")
    if "scale" in text_lower:
        keywords.append("scaling")

    # Exit types
    if "stop loss" in text_lower or "stoploss" in text_lower:
        keywords.append("stop_loss")
    if "take profit" in text_lower:
        keywords.append("take_profit")
    if "trailing" in text_lower:
        keywords.append("trailing_stop")

    return keywords


def categorize_strategy(strategy: Dict[str, Any]) -> str:
    """Categorize strategy type for pattern analysis"""
    if not strategy:
        return "unknown"

    indicators = list(strategy.get("indicators", {}).keys())

    if "rsi" in indicators:
        return "rsi_based"
    elif "macd" in indicators:
        return "macd_based"
    elif any(ind in indicators for ind in ["sma", "ema"]):
        return "moving_average"
    elif "sentiment" in str(strategy).lower():
        return "sentiment_based"
    else:
        return "other"


def get_failure_statistics() -> Dict[str, Any]:
    """
    Analyze evaluation history to find patterns.

    Returns statistics that help identify system bugs:
    - Failure rate by evaluator (which evaluator fails most?)
    - Failure rate by strategy type (RSI strategies fail more?)
    - Common error messages (repeated bugs)
    """
    if not ANALYTICS_FILE.exists():
        return {"error": "No analytics data yet"}

    records = []
    try:
        with open(ANALYTICS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception as e:
        return {"error": f"Failed to read analytics: {e}"}

    if not records:
        return {"error": "No records found"}

    total = len(records)
    passed = sum(1 for r in records if r.get("all_passed"))

    # Failure rate by evaluator
    evaluator_failures = {}
    evaluator_totals = {}
    for record in records:
        for name, details in record.get("evaluator_details", {}).items():
            evaluator_totals[name] = evaluator_totals.get(name, 0) + 1
            if not details.get("passed"):
                evaluator_failures[name] = evaluator_failures.get(name, 0) + 1

    evaluator_failure_rates = {
        name: {
            "failures": evaluator_failures.get(name, 0),
            "total": evaluator_totals[name],
            "failure_rate": round(evaluator_failures.get(name, 0) / evaluator_totals[name] * 100, 1)
        }
        for name in evaluator_totals
    }

    # Failure rate by strategy type
    type_failures = {}
    type_totals = {}
    for record in records:
        stype = record.get("strategy_type", "unknown")
        type_totals[stype] = type_totals.get(stype, 0) + 1
        if not record.get("all_passed"):
            type_failures[stype] = type_failures.get(stype, 0) + 1

    strategy_type_failure_rates = {
        stype: {
            "failures": type_failures.get(stype, 0),
            "total": type_totals[stype],
            "failure_rate": round(type_failures.get(stype, 0) / type_totals[stype] * 100, 1)
        }
        for stype in type_totals
    }

    # Most common errors (indicates repeated bugs)
    error_counts = {}
    for record in records:
        for error in record.get("errors", []):
            # Normalize error message
            error_key = error[:100] if error else "unknown"
            error_counts[error_key] = error_counts.get(error_key, 0) + 1

    top_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Keyword correlation with failures
    keyword_failures = {}
    keyword_totals = {}
    for record in records:
        for keyword in record.get("user_input_keywords", []):
            keyword_totals[keyword] = keyword_totals.get(keyword, 0) + 1
            if not record.get("all_passed"):
                keyword_failures[keyword] = keyword_failures.get(keyword, 0) + 1

    keyword_failure_rates = {
        kw: {
            "failures": keyword_failures.get(kw, 0),
            "total": keyword_totals[kw],
            "failure_rate": round(keyword_failures.get(kw, 0) / keyword_totals[kw] * 100, 1)
        }
        for kw in keyword_totals if keyword_totals[kw] >= 3  # Only show keywords with enough data
    }

    return {
        "summary": {
            "total_evaluations": total,
            "passed": passed,
            "failed": total - passed,
            "overall_pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        },
        "evaluator_failure_rates": evaluator_failure_rates,
        "strategy_type_failure_rates": strategy_type_failure_rates,
        "keyword_failure_rates": keyword_failure_rates,
        "top_errors": top_errors,
        "insight": generate_insight(evaluator_failure_rates, strategy_type_failure_rates, top_errors),
    }


def generate_insight(evaluator_rates: Dict, strategy_rates: Dict, top_errors: List) -> str:
    """Generate human-readable insight about what system bugs to fix"""
    insights = []

    # Find worst evaluator
    worst_eval = max(evaluator_rates.items(), key=lambda x: x[1]["failure_rate"], default=(None, {}))
    if worst_eval[0] and worst_eval[1].get("failure_rate", 0) > 20:
        insights.append(
            f"🔴 {worst_eval[0]} fails {worst_eval[1]['failure_rate']}% of the time - "
            f"investigate the code generator's handling of this evaluator's requirements"
        )

    # Find worst strategy type
    worst_type = max(strategy_rates.items(), key=lambda x: x[1]["failure_rate"], default=(None, {}))
    if worst_type[0] and worst_type[1].get("failure_rate", 0) > 30:
        insights.append(
            f"🔴 {worst_type[0]} strategies fail {worst_type[1]['failure_rate']}% - "
            f"review the code generation templates for this strategy type"
        )

    # Check for repeated errors
    if top_errors and top_errors[0][1] >= 5:
        insights.append(
            f"🔴 Repeated error ({top_errors[0][1]}x): '{top_errors[0][0][:50]}...' - "
            f"this is likely a systematic bug in your code"
        )

    if not insights:
        insights.append("✅ No major patterns detected - system is performing well")

    return " | ".join(insights)


def get_recent_failures(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent evaluation failures for debugging"""
    if not ANALYTICS_FILE.exists():
        return []

    records = []
    try:
        with open(ANALYTICS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if not record.get("all_passed"):
                        records.append(record)
    except Exception as e:
        logger.warning(f"Failed to read analytics: {e}")
        return []

    # Return most recent failures
    return sorted(records, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
