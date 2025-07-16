"""
Main entry point for SentimentGuard (Streamlit app).
"""
import streamlit as st
from data.fetch_tweets import fetch_tweets
from nlp.sentiment_model import analyze_sentiments
from risk_engine.risk_score import calculate_risk_score

st.set_page_config(page_title="SentimentGuard", layout="wide")
st.title("🧠 SentimentGuard - Market Emotion & Risk Analyzer")

# Fetch tweets (stub)
tweets = fetch_tweets()
# Analyze sentiments (stub)
sentiments = analyze_sentiments(tweets)
# Calculate risk score (stub)
score, label, reason = calculate_risk_score(sentiments)

st.metric("Today's Risk Level", f"{label} ({score})")
st.write(f"Reason: {reason}")