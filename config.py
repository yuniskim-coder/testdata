"""
Configuration settings for the weather app
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize variables with deployment fallback
OPENWEATHER_API_KEY = "f4e5ad99faddf91dce8add9f4ec8723f"  # Deployment fallback
DEFAULT_CITY = "Seoul"
DEFAULT_COUNTRY = "KR"
CACHE_TTL_SECONDS = 600

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # For Streamlit Cloud deployment - use secrets
    if hasattr(st, 'secrets'):
        try:
            secrets_key = st.secrets.get("api", {}).get("openweather_key", "")
            if secrets_key:
                OPENWEATHER_API_KEY = secrets_key
            DEFAULT_CITY = st.secrets.get("app", {}).get("default_city", DEFAULT_CITY)
            DEFAULT_COUNTRY = st.secrets.get("app", {}).get("default_country", DEFAULT_COUNTRY)
            CACHE_TTL_SECONDS = int(st.secrets.get("app", {}).get("cache_ttl_seconds", CACHE_TTL_SECONDS))
        except Exception as e:
            print(f"Error reading Streamlit secrets (using fallback): {e}")
            pass
except (ImportError, AttributeError):
    # Streamlit not available or no secrets
    pass

# Override with environment variables if available (for local development)
env_key = os.getenv("OPENWEATHER_API_KEY", "")
if env_key:
    OPENWEATHER_API_KEY = env_key

DEFAULT_CITY = os.getenv("DEFAULT_CITY", DEFAULT_CITY)
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", DEFAULT_COUNTRY)
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", str(CACHE_TTL_SECONDS)))

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