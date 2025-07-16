"""
Computes technical indicators (RSI, MACD, Bollinger Bands) using pandas.
"""
import pandas as pd

def compute_indicators(df):
    """Compute RSI, MACD, and Bollinger Bands. Returns DataFrame with indicators."""
    # Placeholder: add dummy indicator columns
    df = df.copy()
    df["RSI"] = 50
    df["MACD"] = 0
    df["Bollinger_Upper"] = df["Close"] + 5
    df["Bollinger_Lower"] = df["Close"] - 5
    return df

if __name__ == "__main__":
    import sys
    print(compute_indicators(pd.DataFrame({"Close": [100, 101, 102]})))