"""
Plots and visuals for SentimentGuard dashboard (Plotly/Matplotlib).
"""
import plotly.graph_objs as go
import streamlit as st

def plot_sentiment_trend(data):
    """Plot a simple sentiment trend line chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data, mode='lines', name='Sentiment'))
    st.plotly_chart(fig)

if __name__ == "__main__":
    plot_sentiment_trend([1, 2, 3, 2, 1])