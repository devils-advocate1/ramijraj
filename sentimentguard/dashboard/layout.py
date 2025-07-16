"""
Defines UI layout for SentimentGuard dashboard using Streamlit.
"""
import streamlit as st

def render_dashboard(score, label, reason):
    """Render main dashboard layout."""
    st.metric("Today's Risk Level", f"{label} ({score})")
    st.write(f"Reason: {reason}")
    # Add more UI elements as needed

if __name__ == "__main__":
    import random
    render_dashboard(random.randint(0,100), "Medium", "Stub reason")