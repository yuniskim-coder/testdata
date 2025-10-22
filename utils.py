"""
Utility functions for the weather app
"""
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
import streamlit as st

# 한글 도시명 매핑 사전
KOREAN_CITY_MAPPING = {
    # 한국 도시
    "서울": "Seoul,KR",
    "부산": "Busan,KR", 
    "대구": "Daegu,KR",
    "인천": "Incheon,KR",
    "광주": "Gwangju,KR",
    "대전": "Daejeon,KR",
    "울산": "Ulsan,KR",
    "제주": "Jeju,KR",
    "수원": "Suwon,KR",
    "창원": "Changwon,KR",
    "성남": "Seongnam,KR",
    "청주": "Cheongju,KR",
    "전주": "Jeonju,KR",
    "천안": "Cheonan,KR",
    "안산": "Ansan,KR",
    "안양": "Anyang,KR",
    "포항": "Pohang,KR",
    "의정부": "Uijeongbu,KR",
    "원주": "Wonju,KR",
    "춘천": "Chuncheon,KR",
    
    # 일본 주요 도시
    "도쿄": "Tokyo,JP",
    "교토": "Kyoto,JP", 
    "오사카": "Osaka,JP",
    "나고야": "Nagoya,JP",
    "후쿠오카": "Fukuoka,JP",
    "삿포로": "Sapporo,JP",
    "센다이": "Sendai,JP",
    "히로시마": "Hiroshima,JP",
    "요코하마": "Yokohama,JP",
    
    # 중국 주요 도시
    "베이징": "Beijing,CN",
    "상하이": "Shanghai,CN",
    "광저우": "Guangzhou,CN",
    "선전": "Shenzhen,CN",
    "청두": "Chengdu,CN",
    "시안": "Xi'an,CN",
    "난징": "Nanjing,CN",
    "우한": "Wuhan,CN",
    "텐진": "Tianjin,CN",
    "항저우": "Hangzhou,CN",
    
    # 동남아시아
    "방콕": "Bangkok,TH",
    "싱가포르": "Singapore,SG", 
    "쿠알라룸푸르": "Kuala Lumpur,MY",
    "자카르타": "Jakarta,ID",
    "마닐라": "Manila,PH",
    "호치민": "Ho Chi Minh City,VN",
    "하노이": "Hanoi,VN",
    "양곤": "Yangon,MM",
    "프놈펜": "Phnom Penh,KH",
    
    # 유럽 주요 도시
    "런던": "London,GB",
    "파리": "Paris,FR",
    "베를린": "Berlin,DE",
    "로마": "Rome,IT",
    "마드리드": "Madrid,ES",
    "암스테르담": "Amsterdam,NL",
    "취리히": "Zurich,CH",
    "스톡홀름": "Stockholm,SE",
    "비엔나": "Vienna,AT",
    "프라하": "Prague,CZ",
    "바르셀로나": "Barcelona,ES",
    "밀라노": "Milan,IT",
    "뮌헨": "Munich,DE",
    "부다페스트": "Budapest,HU",
    "바르샤바": "Warsaw,PL",
    "오슬로": "Oslo,NO",
    "헬싱키": "Helsinki,FI",
    "코펜하겐": "Copenhagen,DK",
    
    # 북미 주요 도시
    "뉴욕": "New York,US",
    "로스앤젤레스": "Los Angeles,US",
    "시카고": "Chicago,US",
    "휴스턴": "Houston,US",
    "피닉스": "Phoenix,US",
    "필라델피아": "Philadelphia,US",
    "샌안토니오": "San Antonio,US",
    "샌디에이고": "San Diego,US",
    "댈러스": "Dallas,US",
    "산호세": "San Jose,US",
    "라스베이거스": "Las Vegas,US",
    "시애틀": "Seattle,US",
    "덴버": "Denver,US",
    "워싱턴": "Washington,US",
    "보스턴": "Boston,US",
    "토론토": "Toronto,CA",
    "몬트리올": "Montreal,CA",
    "벤쿠버": "Vancouver,CA",
    "캘거리": "Calgary,CA",
    
    # 남미 주요 도시
    "상파울루": "São Paulo,BR",
    "리우데자네이루": "Rio de Janeiro,BR",
    "부에노스아이레스": "Buenos Aires,AR",
    "리마": "Lima,PE",
    "보고타": "Bogotá,CO",
    "산티아고": "Santiago,CL",
    "카라카스": "Caracas,VE",
    
    # 오세아니아
    "시드니": "Sydney,AU",
    "멜버른": "Melbourne,AU",
    "브리즈번": "Brisbane,AU",
    "퍼스": "Perth,AU",
    "애들레이드": "Adelaide,AU",
    "오클랜드": "Auckland,NZ",
    "웰링턴": "Wellington,NZ",
    
    # 중동/아프리카
    "두바이": "Dubai,AE",
    "카이로": "Cairo,EG",
    "이스탄불": "Istanbul,TR",
    "텔아비브": "Tel Aviv,IL",
    "카사블랑카": "Casablanca,MA",
    "케이프타운": "Cape Town,ZA",
    "요하네스버그": "Johannesburg,ZA",
    
    # 기타 아시아
    "뭄바이": "Mumbai,IN",
    "델리": "Delhi,IN",
    "방갈로르": "Bangalore,IN",
    "콜카타": "Kolkata,IN",
    "카라치": "Karachi,PK",
    "라호르": "Lahore,PK",
    "다카": "Dhaka,BD",
    "콜롬보": "Colombo,LK",
    "카트만두": "Kathmandu,NP",
    "타슈켄트": "Tashkent,UZ",
    
    # 대만, 홍콩, 마카오
    "타이베이": "Taipei,TW",
    "가오슝": "Kaohsiung,TW",
    "홍콩": "Hong Kong,HK",
    "마카오": "Macau,MO"
}

def translate_korean_city(city_name: str) -> str:
    """
    한글 도시명을 영문으로 변환
    
    Args:
        city_name: 한글 또는 영문 도시명
        
    Returns:
        변환된 영문 도시명 또는 원본 도시명
    """
    city_name = city_name.strip()
    
    # 한글 도시명 매핑에서 찾기
    if city_name in KOREAN_CITY_MAPPING:
        return KOREAN_CITY_MAPPING[city_name]
    
    # 부분 매칭 시도 (예: "서울시" -> "서울")
    for korean_name, english_name in KOREAN_CITY_MAPPING.items():
        if korean_name in city_name or city_name in korean_name:
            return english_name
    
    # 매핑되지 않으면 원본 반환
    return city_name

def search_korean_cities(query: str) -> list:
    """
    한글 도시명 검색 (자동완성용)
    
    Args:
        query: 검색어
        
    Returns:
        매칭되는 도시명 리스트
    """
    if not query:
        return []
    
    query = query.strip().lower()
    matches = []
    
    for korean_name, english_name in KOREAN_CITY_MAPPING.items():
        # 한글명에서 검색
        if query in korean_name.lower():
            matches.append(f"{korean_name} ({english_name})")
        # 영문명에서도 검색
        elif query in english_name.lower():
            matches.append(f"{korean_name} ({english_name})")
    
    return sorted(matches)[:10]  # 상위 10개만 반환


def parse_location_input(location_str: str) -> Dict[str, str]:
    """
    Parse location input string into API parameters.
    한글 도시명도 지원합니다.
    
    Args:
        location_str: City name, "City,Country", "한글도시명" or "lat,lon" format
        
    Returns:
        Dict with 'q' or 'lat'/'lon' keys for API request
        
    Raises:
        ValueError: If input format is invalid
    """
    if not location_str or not location_str.strip():
        raise ValueError("위치를 입력해주세요.")
    
    location_str = location_str.strip()
    
    # 한글 도시명 번역 시도
    translated = translate_korean_city(location_str)
    if translated != location_str:
        # 한글 도시명이 성공적으로 번역됨
        return {"q": translated}
    
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
    
    # Treat as city name (English or other languages)
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