"""
Utility functions for the weather app
"""
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
import streamlit as st


def parse_location_input(location_str: str) -> Dict[str, str]:
    """
    Parse location input string into API parameters.
    
    Args:
        location_str: City name, "City,Country" or "lat,lon" format
        
    Returns:
        Dict with 'q' or 'lat'/'lon' keys for API request
        
    Raises:
        ValueError: If input format is invalid
    """
    if not location_str or not location_str.strip():
        raise ValueError("위치를 입력해주세요.")
    
    location_str = location_str.strip()
    
    # Check if it's coordinates (lat,lon)
    coord_pattern = r'^-?\d+\.?\d*,-?\d+\.?\d*$'
    if re.match(coord_pattern, location_str):
        try:
            lat_str, lon_str = location_str.split(',')
            lat, lon = float(lat_str), float(lon_str)
            
            # Validate coordinate ranges
            if not (-90 <= lat <= 90):
                raise ValueError("위도는 -90에서 90 사이여야 합니다.")
            if not (-180 <= lon <= 180):
                raise ValueError("경도는 -180에서 180 사이여야 합니다.")
                
            return {"lat": str(lat), "lon": str(lon)}
        except ValueError as e:
            if "위도" in str(e) or "경도" in str(e):
                raise e
            raise ValueError("좌표 형식이 올바르지 않습니다. 예: 37.5665,126.9780")
    
    # Treat as city name
    return {"q": location_str}


def format_temperature(temp: float, unit: str) -> str:
    """Format temperature with appropriate unit symbol."""
    from config import TEMPERATURE_UNITS
    
    symbol = TEMPERATURE_UNITS.get(unit, {}).get("symbol", "°C")
    return f"{temp:.1f}{symbol}"


def format_wind_speed(speed: float, unit: str) -> str:
    """Format wind speed with appropriate unit."""
    if unit == "imperial":
        return f"{speed:.1f} mph"
    else:
        return f"{speed:.1f} m/s"


def format_datetime(timestamp: int, timezone_offset: int = 0) -> str:
    """Format unix timestamp to readable datetime string."""
    dt = datetime.fromtimestamp(timestamp + timezone_offset)
    return dt.strftime("%Y년 %m월 %d일 %H:%M")


def format_timestamp(timestamp: int, format_type: str = "datetime") -> str:
    """
    Format unix timestamp to various readable formats.
    
    Args:
        timestamp: Unix timestamp
        format_type: 'datetime', 'date', 'time', 'short'
    
    Returns:
        Formatted string
    """
    dt = datetime.fromtimestamp(timestamp)
    
    if format_type == "datetime":
        return dt.strftime("%Y년 %m월 %d일 %H:%M")
    elif format_type == "date":
        return dt.strftime("%m월 %d일")
    elif format_type == "time":
        return dt.strftime("%H:%M")
    elif format_type == "short":
        return dt.strftime("%m/%d %H:%M")
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_weather_emoji(weather_main: str, weather_id: int = None) -> str:
    """Get emoji representation of weather condition."""
    weather_emojis = {
        "Clear": "☀️",
        "Clouds": "☁️", 
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️"
    }
    return weather_emojis.get(weather_main, "🌤️")


def create_cache_key(location: Dict[str, str], units: str, endpoint: str) -> str:
    """Create a cache key for API responses."""
    if "q" in location:
        location_part = f"q_{location['q']}"
    else:
        location_part = f"coords_{location['lat']}_{location['lon']}"
    
    return f"{endpoint}_{location_part}_{units}"


def cached_weather_request(cache_key: str, api_func, *args, **kwargs):
    """Wrapper for caching API requests."""
    try:
        # Use st.cache_data with proper error handling
        @st.cache_data(ttl=600, show_spinner=False)
        def _cached_request(cache_key: str):
            return api_func(*args, **kwargs)
        
        return _cached_request(cache_key)
    except Exception as e:
        # If caching fails, call the function directly
        return api_func(*args, **kwargs)