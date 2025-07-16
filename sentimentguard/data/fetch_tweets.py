"""
Fetches tweets containing market-related keywords using Tweepy or a placeholder.
Outputs a list of tweet texts.
"""
import logging

def fetch_tweets(keywords=None, max_tweets=10):
    """Fetch tweets containing specified keywords. Returns list of tweet texts."""
    logging.info("Fetching tweets...")
    # Placeholder: return dummy tweets for now
    if keywords is None:
        keywords = ["Nifty", "Bitcoin", "Sell", "Crash"]
    tweets = [f"Sample tweet about {kw}" for kw in keywords for _ in range(2)]
    return tweets[:max_tweets]

if __name__ == "__main__":
    print(fetch_tweets())