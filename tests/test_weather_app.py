"""
Unit tests for weather app utilities
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import parse_location_input, format_temperature, get_weather_emoji
from api import WeatherAPI, WeatherAPIError, get_weather_api


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_parse_location_city(self):
        """Test parsing city names"""
        result = parse_location_input("Seoul,KR")
        self.assertEqual(result, {"q": "Seoul,KR"})
        
        result = parse_location_input("Seoul")
        self.assertEqual(result, {"q": "Seoul"})
    
    def test_parse_location_coordinates(self):
        """Test parsing coordinates"""
        result = parse_location_input("37.5665,126.9780")
        self.assertEqual(result, {"lat": "37.5665", "lon": "126.9780"})
        
        result = parse_location_input("-90.0,-180.0")
        self.assertEqual(result, {"lat": "-90.0", "lon": "-180.0"})
    
    def test_parse_location_invalid(self):
        """Test invalid location inputs"""
        with self.assertRaises(ValueError):
            parse_location_input("")
        
        with self.assertRaises(ValueError):
            parse_location_input("91.0,0.0")  # Invalid latitude
        
        with self.assertRaises(ValueError):
            parse_location_input("0.0,181.0")  # Invalid longitude
    
    def test_format_temperature(self):
        """Test temperature formatting"""
        self.assertEqual(format_temperature(25.5, "metric"), "25.5°C")
        self.assertEqual(format_temperature(77.9, "imperial"), "77.9°F")
        self.assertEqual(format_temperature(298.65, "standard"), "298.7K")
    
    def test_get_weather_emoji(self):
        """Test weather emoji selection"""
        self.assertEqual(get_weather_emoji("Clear", 800), "☀️")
        self.assertEqual(get_weather_emoji("Rain", 500), "🌧️")
        self.assertEqual(get_weather_emoji("Unknown", 999), "🌤️")


class TestWeatherAPI(unittest.TestCase):
    """Test Weather API functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = WeatherAPI("test_key")
    
    @patch('requests.get')
    def test_api_success(self, mock_get):
        """Test successful API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Seoul',
            'sys': {'country': 'KR'},
            'dt': 1634567890,
            'timezone': 32400,
            'weather': [{'main': 'Clear', 'description': '맑음', 'icon': '01d'}],
            'main': {
                'temp': 25.5,
                'feels_like': 24.0,
                'humidity': 60,
                'pressure': 1013
            },
            'wind': {'speed': 2.5, 'deg': 180},
            'coord': {'lat': 37.5665, 'lon': 126.9780}
        }
        mock_get.return_value = mock_response
        
        location = {"q": "Seoul,KR"}
        result = self.api.get_current_weather(location)
        
        self.assertEqual(result.city, "Seoul")
        self.assertEqual(result.country, "KR")
        self.assertEqual(result.temperature, 25.5)
    
    @patch('requests.get')
    def test_api_invalid_key(self, mock_get):
        """Test API error handling for invalid key"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        location = {"q": "Seoul,KR"}
        with self.assertRaises(WeatherAPIError):
            self.api.get_current_weather(location)
    
    @patch('requests.get')
    def test_api_city_not_found(self, mock_get):
        """Test API error handling for city not found"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        location = {"q": "InvalidCity"}
        with self.assertRaises(WeatherAPIError):
            self.api.get_current_weather(location)


if __name__ == '__main__':
    unittest.main()