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
    pop: float = 0.0  # 강수 확률 추가
    
    
@dataclass
class HourlyForecastData:
    """Data class for hourly forecast (minutely alternative)"""
    timestamp: int
    temperature: float
    feels_like: float
    weather_main: str
    weather_description: str
    weather_icon: str
    humidity: int
    wind_speed: float
    precipitation: float


@dataclass
class DailyForecastData:
    """Data class for daily forecast information"""
    timestamp: int
    temp_day: float
    temp_min: float
    temp_max: float
    temp_night: float
    temp_eve: float
    temp_morn: float
    feels_like_day: float
    humidity: int
    wind_speed: float
    weather_main: str
    weather_description: str
    weather_icon: str
    sunrise: int
    sunset: int
    uvi: float


@dataclass 
class WeeklyForecastData:
    """Data class for 7-day weekly forecast"""
    daily_forecasts: List[DailyForecastData]


class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""
    pass


class WeatherAPI:
    """OpenWeather API client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENWEATHER_API_KEY
        # Don't raise error during initialization for deployment
        # Error will be raised when making actual API calls
    
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
        # Check API key here instead of __init__
        if not self.api_key:
            raise WeatherAPIError("API 키가 설정되지 않았습니다. Streamlit Secrets에서 API 키를 설정해주세요.")
        
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

    def get_weekly_forecast(self, location: Dict[str, str], units: str = "metric") -> WeeklyForecastData:
        """
        Get 7-day weekly weather forecast using OneCall API
        
        Args:
            location: Dict with 'q' (city name) or 'lat'/'lon' (coordinates)
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            WeeklyForecastData object with 7-day forecast
        """
        # First get coordinates if city name provided
        if 'q' in location:
            current_weather = self.get_current_weather(location, units)
            lat, lon = current_weather.lat, current_weather.lon
        else:
            lat, lon = location['lat'], location['lon']
        
        # Use OneCall API for detailed 7-day forecast
        params = {
            'lat': lat,
            'lon': lon,
            'units': units,
            'lang': 'kr',
            'exclude': 'current,minutely,alerts'  # Only get daily and hourly
        }
        
        try:
            response_data = self._make_request("onecall", params)
        except WeatherAPIError:
            # OneCall API 접근 불가 시 기본 forecast API 사용
            logger.info("OneCall API 사용 불가, 기본 forecast API로 대체")
            daily_basic = self.get_daily_forecast(location, units, days=5)
            daily_forecasts = []
            for day in daily_basic:
                daily_forecasts.append(DailyForecastData(
                    timestamp=int(time.mktime(time.strptime(day['date'], '%Y-%m-%d'))),
                    temp_day=day['temp_avg'],
                    temp_min=day['temp_min'],
                    temp_max=day['temp_max'],
                    temp_night=day['temp_min'],
                    temp_eve=day['temp_avg'],
                    temp_morn=day['temp_avg'],
                    feels_like_day=day['temp_avg'],
                    humidity=int(day['humidity_avg']),
                    wind_speed=day['wind_speed_avg'],
                    weather_main=day['weather_description'],
                    weather_description=day['weather_description'],
                    weather_icon=day['weather_icon'],
                    sunrise=0,
                    sunset=0,
                    uvi=0.0
                ))
            return WeeklyForecastData(daily_forecasts=daily_forecasts)
        
        # Parse OneCall API response
        daily_forecasts = []
        for day_data in response_data.get('daily', [])[:7]:
            daily_forecasts.append(DailyForecastData(
                timestamp=day_data['dt'],
                temp_day=day_data['temp']['day'],
                temp_min=day_data['temp']['min'],
                temp_max=day_data['temp']['max'],
                temp_night=day_data['temp']['night'],
                temp_eve=day_data['temp']['eve'],
                temp_morn=day_data['temp']['morn'],
                feels_like_day=day_data['feels_like']['day'],
                humidity=day_data['humidity'],
                wind_speed=day_data['wind_speed'],
                weather_main=day_data['weather'][0]['main'],
                weather_description=day_data['weather'][0]['description'],
                weather_icon=day_data['weather'][0]['icon'],
                sunrise=day_data['sunrise'],
                sunset=day_data['sunset'],
                uvi=day_data['uvi']
            ))
        
        return WeeklyForecastData(daily_forecasts=daily_forecasts)

    def get_hourly_forecast(self, location: Dict[str, str], units: str = "metric", hours: int = 24) -> List[HourlyForecastData]:
        """
        Get hourly weather forecast (as alternative to minutely)
        
        Args:
            location: Dict with 'q' (city name) or 'lat'/'lon' (coordinates)
            units: Temperature units ('metric', 'imperial', 'standard')
            hours: Number of hours to forecast (max 48)
            
        Returns:
            List of HourlyForecastData objects
        """
        # First get coordinates if city name provided
        if 'q' in location:
            current_weather = self.get_current_weather(location, units)
            lat, lon = current_weather.lat, current_weather.lon
        else:
            lat, lon = location['lat'], location['lon']
        
        # Use OneCall API for hourly forecast
        params = {
            'lat': lat,
            'lon': lon,
            'units': units,
            'lang': 'kr',
            'exclude': 'current,daily,minutely,alerts'
        }
        
        try:
            response_data = self._make_request("onecall", params)
        except WeatherAPIError:
            # Fallback to basic forecast converted to hourly
            basic_forecasts = self.get_forecast(location, units)
            hourly_forecasts = []
            for forecast in basic_forecasts[:min(hours, len(basic_forecasts))]:
                hourly_forecasts.append(HourlyForecastData(
                    timestamp=forecast.timestamp,
                    temperature=forecast.temperature,
                    feels_like=forecast.temperature,
                    weather_main=forecast.weather_main,
                    weather_description=forecast.weather_description,
                    weather_icon=forecast.weather_icon,
                    humidity=forecast.humidity,
                    wind_speed=forecast.wind_speed,
                    precipitation=forecast.pop * 10  # Convert percentage to mm estimate
                ))
            return hourly_forecasts
        
        # Parse OneCall API response
        hourly_forecasts = []
        for hour_data in response_data.get('hourly', [])[:hours]:
            precipitation = 0
            if 'rain' in hour_data:
                precipitation += hour_data['rain'].get('1h', 0)
            if 'snow' in hour_data:
                precipitation += hour_data['snow'].get('1h', 0)
                
            hourly_forecasts.append(HourlyForecastData(
                timestamp=hour_data['dt'],
                temperature=hour_data['temp'],
                feels_like=hour_data['feels_like'],
                weather_main=hour_data['weather'][0]['main'],
                weather_description=hour_data['weather'][0]['description'],
                weather_icon=hour_data['weather'][0]['icon'],
                humidity=hour_data['humidity'],
                wind_speed=hour_data['wind_speed'],
                precipitation=precipitation
            ))
        
        return hourly_forecasts

    def get_multiple_cities_weather(self, cities: List[Dict[str, str]], units: str = "metric") -> List[WeatherData]:
        """
        Get current weather for multiple cities
        
        Args:
            cities: List of location dicts with 'q' (city name) or 'lat'/'lon'
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            List of WeatherData objects
        """
        weather_data = []
        for city in cities:
            try:
                weather = self.get_current_weather(city, units)
                weather_data.append(weather)
            except WeatherAPIError as e:
                logger.warning(f"Failed to get weather for {city}: {e}")
                continue
        
        return weather_data


# Create a global instance only when API key is available
weather_api = None

def get_weather_api():
    """Get or create weather API instance"""
    global weather_api
    if weather_api is None:
        from config import OPENWEATHER_API_KEY
        weather_api = WeatherAPI(api_key=OPENWEATHER_API_KEY)
    return weather_api