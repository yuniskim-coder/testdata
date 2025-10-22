"""
Configuration settings for the weather app
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # For Streamlit Cloud deployment - use secrets
    OPENWEATHER_API_KEY = st.secrets.get("api", {}).get("openweather_key", "") or os.getenv("OPENWEATHER_API_KEY", "")
    DEFAULT_CITY = st.secrets.get("app", {}).get("default_city", "Seoul") or os.getenv("DEFAULT_CITY", "Seoul")
    DEFAULT_COUNTRY = st.secrets.get("app", {}).get("default_country", "KR") or os.getenv("DEFAULT_COUNTRY", "KR")
    CACHE_TTL_SECONDS = int(st.secrets.get("app", {}).get("cache_ttl_seconds", 600) or os.getenv("CACHE_TTL_SECONDS", "600"))
except (ImportError, AttributeError):
    # For local development - use environment variables
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Seoul")
    DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "KR")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))

# API Configuration
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"

# API Settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2

# UI Settings
TEMPERATURE_UNITS = {
    "metric": {"name": "섭씨 (°C)", "symbol": "°C"},
    "imperial": {"name": "화씨 (°F)", "symbol": "°F"},
    "standard": {"name": "켈빈 (K)", "symbol": "K"}
}