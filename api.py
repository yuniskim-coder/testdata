"""
OpenWeather API client with error handling and retry logic
"""
import requests
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging

from config import (
    OPENWEATHER_API_KEY, 
    OPENWEATHER_BASE_URL, 
    REQUEST_TIMEOUT, 
    MAX_RETRIES
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Data class for current weather information"""
    city: str
    country: str
    timestamp: int
    timezone_offset: int
    weather_main: str
    weather_description: str
    weather_icon: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_deg: Optional[int]
    visibility: Optional[int]
    lat: float
    lon: float


@dataclass
class ForecastData:
    """Data class for forecast information"""
    timestamp: int
    temperature: float
    temp_min: float
    temp_max: float
    weather_main: str
    weather_description: str
    weather_icon: str
    humidity: int
    wind_speed: float
    pop: float  # Probability of precipitation


class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""
    pass


class WeatherAPI:
    """OpenWeather API client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENWEATHER_API_KEY
        if not self.api_key:
            raise WeatherAPIError("API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            endpoint: API endpoint (e.g., 'weather', 'forecast')
            params: Request parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            WeatherAPIError: If request fails after retries
        """
        url = f"{OPENWEATHER_BASE_URL}/{endpoint}"
        params['appid'] = self.api_key
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"API 요청 시도 {attempt + 1}: {endpoint}")
                
                response = requests.get(
                    url, 
                    params=params, 
                    timeout=REQUEST_TIMEOUT
                )
                
                # Check for API errors
                if response.status_code == 401:
                    raise WeatherAPIError("API 키가 유효하지 않습니다.")
                elif response.status_code == 404:
                    raise WeatherAPIError("요청한 도시를 찾을 수 없습니다. 도시명을 확인해주세요.")
                elif response.status_code == 429:
                    raise WeatherAPIError("API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
                elif response.status_code >= 400:
                    raise WeatherAPIError(f"API 오류 (코드: {response.status_code})")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"요청 타임아웃 (시도 {attempt + 1})")
                if attempt == MAX_RETRIES:
                    raise WeatherAPIError("요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.")
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"연결 오류 (시도 {attempt + 1})")
                if attempt == MAX_RETRIES:
                    raise WeatherAPIError("서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"요청 오류: {e}")
                if attempt == MAX_RETRIES:
                    raise WeatherAPIError(f"요청 중 오류가 발생했습니다: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < MAX_RETRIES:
                wait_time = 2 ** attempt
                logger.info(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
    
    def get_current_weather(self, location: Dict[str, str], units: str = "metric") -> WeatherData:
        """
        Get current weather data
        
        Args:
            location: Dict with 'q' (city name) or 'lat'/'lon' (coordinates)
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            WeatherData object with current weather information
        """
        params = {
            'units': units,
            'lang': 'kr'  # Korean language for descriptions
        }
        params.update(location)
        
        data = self._make_request('weather', params)
        
        return WeatherData(
            city=data['name'],
            country=data['sys']['country'],
            timestamp=data['dt'],
            timezone_offset=data.get('timezone', 0),
            weather_main=data['weather'][0]['main'],
            weather_description=data['weather'][0]['description'],
            weather_icon=data['weather'][0]['icon'],
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data.get('wind', {}).get('speed', 0),
            wind_deg=data.get('wind', {}).get('deg'),
            visibility=data.get('visibility'),
            lat=data['coord']['lat'],
            lon=data['coord']['lon']
        )
    
    def get_forecast(self, location: Dict[str, str], units: str = "metric") -> List[ForecastData]:
        """
        Get 5-day weather forecast
        
        Args:
            location: Dict with 'q' (city name) or 'lat'/'lon' (coordinates)
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            List of ForecastData objects (up to 40 entries, 3-hour intervals)
        """
        params = {
            'units': units,
            'lang': 'kr'
        }
        params.update(location)
        
        data = self._make_request('forecast', params)
        
        forecasts = []
        for item in data['list']:
            forecasts.append(ForecastData(
                timestamp=item['dt'],
                temperature=item['main']['temp'],
                temp_min=item['main']['temp_min'],
                temp_max=item['main']['temp_max'],
                weather_main=item['weather'][0]['main'],
                weather_description=item['weather'][0]['description'],
                weather_icon=item['weather'][0]['icon'],
                humidity=item['main']['humidity'],
                wind_speed=item.get('wind', {}).get('speed', 0),
                pop=item.get('pop', 0) * 100  # Convert to percentage
            ))
        
        return forecasts
    
    def get_daily_forecast(self, location: Dict[str, str], units: str = "metric", days: int = 5) -> List[Dict]:
        """
        Get daily weather forecast summary (aggregated from 3-hour forecasts)
        
        Args:
            location: Dict with 'q' (city name) or 'lat'/'lon' (coordinates)
            units: Temperature units ('metric', 'imperial', 'standard')
            days: Number of days to forecast (max 5)
            
        Returns:
            List of daily forecast dictionaries
        """
        forecasts = self.get_forecast(location, units)
        
        # Group forecasts by date
        daily_data = {}
        for forecast in forecasts:
            date = time.strftime('%Y-%m-%d', time.gmtime(forecast.timestamp))
            
            if date not in daily_data:
                daily_data[date] = {
                    'date': date,
                    'temps': [],
                    'descriptions': [],
                    'icons': [],
                    'humidity': [],
                    'wind_speeds': [],
                    'pop': []
                }
            
            daily_data[date]['temps'].append(forecast.temperature)
            daily_data[date]['descriptions'].append(forecast.weather_description)
            daily_data[date]['icons'].append(forecast.weather_icon)
            daily_data[date]['humidity'].append(forecast.humidity)
            daily_data[date]['wind_speeds'].append(forecast.wind_speed)
            daily_data[date]['pop'].append(forecast.pop)
        
        # Aggregate daily data
        daily_forecasts = []
        for date, data in list(daily_data.items())[:days]:
            # Find most common weather condition
            icon_counts = {}
            for icon in data['icons']:
                icon_counts[icon] = icon_counts.get(icon, 0) + 1
            most_common_icon = max(icon_counts.items(), key=lambda x: x[1])[0]
            
            daily_forecasts.append({
                'date': date,
                'temp_min': min(data['temps']),
                'temp_max': max(data['temps']),
                'temp_avg': sum(data['temps']) / len(data['temps']),
                'weather_icon': most_common_icon,
                'weather_description': data['descriptions'][0],  # Take first description
                'humidity_avg': sum(data['humidity']) / len(data['humidity']),
                'wind_speed_avg': sum(data['wind_speeds']) / len(data['wind_speeds']),
                'pop_max': max(data['pop']) if data['pop'] else 0
            })
        
        return daily_forecasts


# Create a global instance
weather_api = WeatherAPI()