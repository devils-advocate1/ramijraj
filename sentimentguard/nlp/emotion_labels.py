"""
Maps sentiment labels to emotion categories (Fear, Greed, etc.) and attaches timestamps.
"""
from datetime import datetime

def map_to_emotions(sentiments):
    """Convert sentiment tuples to emotion labels with timestamps."""
    mapping = {
        "Positive": ["Greed", "FOMO"],
        "Negative": ["Fear", "Panic"],
        "Neutral": ["Calm", "Stable"]
    }
    results = []
    for text, sentiment, score in sentiments:
        emotions = mapping.get(sentiment, ["Unknown"])
        results.append({
            "text": text,
            "sentiment": sentiment,
            "emotions": emotions,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
    return results

if __name__ == "__main__":
    print(map_to_emotions([("Test", "Positive", 0.9)]))