"""
Local storage system for weather app data
Handles favorites, search history, and saved weather records
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# Storage file paths
STORAGE_DIR = "data"
FAVORITES_FILE = os.path.join(STORAGE_DIR, "favorites.json")
HISTORY_FILE = os.path.join(STORAGE_DIR, "search_history.json")
SAVED_WEATHER_FILE = os.path.join(STORAGE_DIR, "saved_weather.json")

@dataclass
class SavedWeatherRecord:
    """Data class for saved weather records"""
    location: str
    timestamp: str
    weather_data: Dict[str, Any]
    user_note: Optional[str] = None
    
@dataclass
class FavoriteLocation:
    """Data class for favorite locations"""
    name: str
    query: str  # Location query string
    lat: Optional[float] = None
    lon: Optional[float] = None
    added_date: Optional[str] = None

@dataclass 
class SearchHistoryItem:
    """Data class for search history items"""
    query: str
    timestamp: str
    success: bool = True

class WeatherStorage:
    """Local storage manager for weather app data"""
    
    def __init__(self):
        """Initialize storage and create data directory if needed"""
        self._ensure_storage_dir()
        
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
            logger.info(f"Created storage directory: {STORAGE_DIR}")
    
    def _load_json(self, filepath: str, default: Any = None) -> Any:
        """Load JSON data from file with error handling"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading {filepath}: {e}")
        
        return default if default is not None else []
    
    def _save_json(self, filepath: str, data: Any) -> bool:
        """Save data to JSON file with error handling"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error saving {filepath}: {e}")
            return False
    
    # Favorites management
    def get_favorites(self) -> List[FavoriteLocation]:
        """Get all favorite locations"""
        data = self._load_json(FAVORITES_FILE, [])
        return [FavoriteLocation(**item) for item in data]
    
    def add_favorite(self, name: str, query: str, lat: float = None, lon: float = None) -> bool:
        """Add a location to favorites"""
        favorites = self.get_favorites()
        
        # Check if already exists
        for fav in favorites:
            if fav.query.lower() == query.lower():
                logger.info(f"Location {query} already in favorites")
                return False
        
        new_favorite = FavoriteLocation(
            name=name,
            query=query,
            lat=lat,
            lon=lon,
            added_date=datetime.now().isoformat()
        )
        
        favorites.append(new_favorite)
        data = [asdict(fav) for fav in favorites]
        return self._save_json(FAVORITES_FILE, data)
    
    def remove_favorite(self, query: str) -> bool:
        """Remove a location from favorites"""
        favorites = self.get_favorites()
        original_count = len(favorites)
        
        favorites = [fav for fav in favorites if fav.query.lower() != query.lower()]
        
        if len(favorites) < original_count:
            data = [asdict(fav) for fav in favorites]
            return self._save_json(FAVORITES_FILE, data)
        
        return False
    
    def is_favorite(self, query: str) -> bool:
        """Check if location is in favorites"""
        favorites = self.get_favorites()
        return any(fav.query.lower() == query.lower() for fav in favorites)
    
    # Search history management
    def get_search_history(self, limit: int = 20) -> List[SearchHistoryItem]:
        """Get recent search history"""
        data = self._load_json(HISTORY_FILE, [])
        history = [SearchHistoryItem(**item) for item in data]
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def add_search_history(self, query: str, success: bool = True) -> bool:
        """Add search to history"""
        history = self.get_search_history(100)  # Keep last 100
        
        # Remove duplicates of same query
        history = [item for item in history if item.query.lower() != query.lower()]
        
        new_item = SearchHistoryItem(
            query=query,
            timestamp=datetime.now().isoformat(),
            success=success
        )
        
        history.insert(0, new_item)  # Add to beginning
        history = history[:50]  # Keep only 50 most recent
        
        data = [asdict(item) for item in history]
        return self._save_json(HISTORY_FILE, data)
    
    def clear_search_history(self) -> bool:
        """Clear all search history"""
        return self._save_json(HISTORY_FILE, [])
    
    # Saved weather records management
    def get_saved_weather(self, limit: int = 50) -> List[SavedWeatherRecord]:
        """Get saved weather records"""
        data = self._load_json(SAVED_WEATHER_FILE, [])
        records = [SavedWeatherRecord(**item) for item in data]
        return sorted(records, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def save_weather_record(self, location: str, weather_data: Dict[str, Any], note: str = None) -> bool:
        """Save a weather record with optional note"""
        records = self.get_saved_weather(200)  # Keep last 200
        
        new_record = SavedWeatherRecord(
            location=location,
            timestamp=datetime.now().isoformat(),
            weather_data=weather_data,
            user_note=note
        )
        
        records.insert(0, new_record)  # Add to beginning
        records = records[:100]  # Keep only 100 most recent
        
        data = [asdict(record) for record in records]
        return self._save_json(SAVED_WEATHER_FILE, data)
    
    def delete_weather_record(self, timestamp: str) -> bool:
        """Delete a specific weather record"""
        records = self.get_saved_weather()
        original_count = len(records)
        
        records = [record for record in records if record.timestamp != timestamp]
        
        if len(records) < original_count:
            data = [asdict(record) for record in records]
            return self._save_json(SAVED_WEATHER_FILE, data)
        
        return False
    
    def get_weather_records_by_location(self, location: str) -> List[SavedWeatherRecord]:
        """Get all weather records for a specific location"""
        records = self.get_saved_weather()
        return [record for record in records if record.location.lower() == location.lower()]
    
    # Utility methods
    def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics"""
        return {
            'favorites_count': len(self.get_favorites()),
            'history_count': len(self.get_search_history(1000)),
            'saved_weather_count': len(self.get_saved_weather(1000))
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export all data for backup"""
        return {
            'favorites': [asdict(fav) for fav in self.get_favorites()],
            'history': [asdict(item) for item in self.get_search_history(1000)],
            'saved_weather': [asdict(record) for record in self.get_saved_weather(1000)],
            'export_date': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """Import data from backup"""
        try:
            if 'favorites' in data:
                self._save_json(FAVORITES_FILE, data['favorites'])
            if 'history' in data:
                self._save_json(HISTORY_FILE, data['history'])
            if 'saved_weather' in data:
                self._save_json(SAVED_WEATHER_FILE, data['saved_weather'])
            return True
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False

# Global storage instance
storage = WeatherStorage()