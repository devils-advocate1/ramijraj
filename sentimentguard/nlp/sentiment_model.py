"""
Loads a pretrained sentiment model and classifies tweet sentiments.
"""
import logging

def analyze_sentiments(tweets):
    """Analyze sentiments of tweets. Returns list of (text, sentiment, score)."""
    logging.info("Analyzing sentiments...")
    # Placeholder: assign random sentiments
    results = []
    for t in tweets:
        results.append((t, "Positive", 0.95))
    return results

if __name__ == "__main__":
    print(analyze_sentiments(["Test tweet 1", "Test tweet 2"]))