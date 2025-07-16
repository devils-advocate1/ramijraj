"""
Fetches OHLCV market data using yfinance or Alpha Vantage.
"""
import pandas as pd

def fetch_market_data(symbol="AAPL", days=7):
    """Fetch OHLCV data for the given symbol and days. Returns DataFrame."""
    # Placeholder: create dummy data
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    data = pd.DataFrame({
        "Open": [100 + i for i in range(days)],
        "High": [105 + i for i in range(days)],
        "Low": [95 + i for i in range(days)],
        "Close": [102 + i for i in range(days)],
        "Volume": [1000 + 10*i for i in range(days)]
    }, index=dates)
    return data

if __name__ == "__main__":
    print(fetch_market_data())