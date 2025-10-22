"""
Location services for weather app
Handles geolocation, location detection, and coordinate management
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)

def get_geolocation_component():
    """Generate HTML/JS component for geolocation"""
    return """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    // Send location data to Streamlit
                    window.parent.postMessage({
                        type: 'geolocation',
                        latitude: lat,
                        longitude: lon,
                        accuracy: accuracy
                    }, '*');
                },
                function(error) {
                    let errorMsg = "";
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = "위치 접근이 거부되었습니다.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = "위치 정보를 사용할 수 없습니다.";
                            break;
                        case error.TIMEOUT:
                            errorMsg = "위치 요청 시간이 초과되었습니다.";
                            break;
                        default:
                            errorMsg = "알 수 없는 오류가 발생했습니다.";
                    }
                    
                    window.parent.postMessage({
                        type: 'geolocation_error',
                        error: errorMsg
                    }, '*');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000  // 5 minutes
                }
            );
        } else {
            window.parent.postMessage({
                type: 'geolocation_error',
                error: '이 브라우저는 위치 서비스를 지원하지 않습니다.'
            }, '*');
        }
    }
    
    // Automatically start geolocation when component loads
    window.addEventListener('load', function() {
        getLocation();
    });
    </script>
    
    <div id="geolocation-status">
        <p>📍 현재 위치를 가져오는 중...</p>
        <button onclick="getLocation()" style="
            background: #ff4b4b;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        ">📍 내 위치 다시 가져오기</button>
    </div>
    """

class LocationService:
    """Location service manager"""
    
    def __init__(self):
        """Initialize location service"""
        if 'user_location' not in st.session_state:
            st.session_state.user_location = None
        if 'location_error' not in st.session_state:
            st.session_state.location_error = None
    
    def get_user_location(self) -> Optional[Tuple[float, float]]:
        """Get user's current location from session state"""
        if st.session_state.user_location:
            return (
                st.session_state.user_location['latitude'],
                st.session_state.user_location['longitude']
            )
        return None
    
    def set_user_location(self, lat: float, lon: float, accuracy: float = None):
        """Set user location in session state"""
        st.session_state.user_location = {
            'latitude': lat,
            'longitude': lon,
            'accuracy': accuracy,
            'timestamp': st.session_state.get('timestamp', None)
        }
        st.session_state.location_error = None
        logger.info(f"User location set: {lat}, {lon}")
    
    def set_location_error(self, error: str):
        """Set location error in session state"""
        st.session_state.location_error = error
        st.session_state.user_location = None
        logger.warning(f"Location error: {error}")
    
    def has_location(self) -> bool:
        """Check if user location is available"""
        return st.session_state.user_location is not None
    
    def get_location_error(self) -> Optional[str]:
        """Get location error if any"""
        return st.session_state.location_error
    
    def render_location_component(self):
        """Render the geolocation component"""
        components.html(get_geolocation_component(), height=100)
    
    def get_location_query(self) -> Optional[Dict[str, float]]:
        """Get location query dict for API calls"""
        location = self.get_user_location()
        if location:
            return {
                'lat': location[0],
                'lon': location[1]
            }
        return None
    
    def format_location_string(self) -> str:
        """Format location for display"""
        location = self.get_user_location()
        if location:
            lat, lon = location
            return f"📍 현재 위치 ({lat:.3f}, {lon:.3f})"
        return "📍 위치 정보 없음"

# Popular cities for quick access
POPULAR_CITIES = {
    "🇰🇷 한국": [
        {"name": "서울", "query": "Seoul,KR"},
        {"name": "부산", "query": "Busan,KR"},
        {"name": "대구", "query": "Daegu,KR"},
        {"name": "인천", "query": "Incheon,KR"},
        {"name": "광주", "query": "Gwangju,KR"},
        {"name": "대전", "query": "Daejeon,KR"},
        {"name": "울산", "query": "Ulsan,KR"},
        {"name": "제주", "query": "Jeju,KR"},
    ],
    "🌏 아시아": [
        {"name": "도쿄", "query": "Tokyo,JP"},
        {"name": "베이징", "query": "Beijing,CN"},
        {"name": "상하이", "query": "Shanghai,CN"},
        {"name": "방콕", "query": "Bangkok,TH"},
        {"name": "싱가포르", "query": "Singapore,SG"},
        {"name": "홍콩", "query": "Hong Kong,HK"},
        {"name": "타이베이", "query": "Taipei,TW"},
        {"name": "자카르타", "query": "Jakarta,ID"},
    ],
    "🌍 유럽": [
        {"name": "런던", "query": "London,GB"},
        {"name": "파리", "query": "Paris,FR"},
        {"name": "베를린", "query": "Berlin,DE"},
        {"name": "로마", "query": "Rome,IT"},
        {"name": "마드리드", "query": "Madrid,ES"},
        {"name": "암스테르담", "query": "Amsterdam,NL"},
        {"name": "취리히", "query": "Zurich,CH"},
        {"name": "스톡홀름", "query": "Stockholm,SE"},
    ],
    "🌎 아메리카": [
        {"name": "뉴욕", "query": "New York,US"},
        {"name": "로스앤젤레스", "query": "Los Angeles,US"},
        {"name": "토론토", "query": "Toronto,CA"},
        {"name": "멕시코시티", "query": "Mexico City,MX"},
        {"name": "상파울루", "query": "São Paulo,BR"},
        {"name": "부에노스아이레스", "query": "Buenos Aires,AR"},
        {"name": "시카고", "query": "Chicago,US"},
        {"name": "마이애미", "query": "Miami,US"},
    ]
}

def get_popular_cities() -> Dict[str, list]:
    """Get popular cities dictionary"""
    return POPULAR_CITIES

# Global location service instance
location_service = LocationService()