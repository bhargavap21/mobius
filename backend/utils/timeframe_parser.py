"""
Utility to parse natural language timeframe descriptions into days
"""
import re
from typing import Optional


def parse_timeframe_to_days(timeframe: str) -> Optional[int]:
    """
    Convert natural language timeframe to number of days

    Examples:
        "90 days" -> 90
        "3 months" -> 90
        "6 months" -> 180
        "1 year" -> 365
        "2 years" -> 730

    Returns:
        Number of days, or None if unable to parse
    """
    if not timeframe:
        return None

    timeframe = timeframe.lower().strip()

    # Direct day patterns: "90 days", "30 days", etc.
    day_match = re.search(r'(\d+)\s*days?', timeframe)
    if day_match:
        return int(day_match.group(1))

    # Month patterns: "3 months", "6 months", etc.
    month_match = re.search(r'(\d+)\s*months?', timeframe)
    if month_match:
        months = int(month_match.group(1))
        return months * 30  # Approximate to 30 days per month

    # Year patterns: "1 year", "2 years", etc.
    year_match = re.search(r'(\d+)\s*years?', timeframe)
    if year_match:
        years = int(year_match.group(1))
        return years * 365

    # Week patterns: "4 weeks", "12 weeks", etc.
    week_match = re.search(r'(\d+)\s*weeks?', timeframe)
    if week_match:
        weeks = int(week_match.group(1))
        return weeks * 7

    # Special cases
    if 'quarter' in timeframe:
        quarters = re.search(r'(\d+)', timeframe)
        if quarters:
            return int(quarters.group(1)) * 90
        return 90  # Default to 1 quarter

    # If we can't parse, return None
    return None
