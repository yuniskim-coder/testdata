"""
Configuration settings for the weather app
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"

# App Configuration
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Seoul")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "KR")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))

# API Settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2

# UI Settings
TEMPERATURE_UNITS = {
    "metric": {"name": "섭씨 (°C)", "symbol": "°C"},
    "imperial": {"name": "화씨 (°F)", "symbol": "°F"},
    "standard": {"name": "켈빈 (K)", "symbol": "K"}
}