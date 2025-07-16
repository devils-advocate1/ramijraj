"""
Common helper functions for SentimentGuard.
"""
from datetime import datetime

def parse_date(date_str):
    """Parse a date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

if __name__ == "__main__":
    print(parse_date("2023-01-01T12:00:00"))