"""
Configuration loader for SentimentGuard.
Loads environment variables and global constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')

# Alpha Vantage API
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')

# Risk thresholds
RISK_THRESHOLDS = {
    'low': 30,
    'medium': 70,
    'high': 100
}