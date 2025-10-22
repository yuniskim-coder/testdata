"""
Streamlit Weather App - 고급 날씨 정보를 시각화하는 웹 애플리케이션
새로운 기능: 주간/일간/시간별 예보, 현재 위치, 즐겨찾기, 검색 히스토리
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
import logging

from api import get_weather_api, WeatherAPIError
try:
    from api import WeeklyForecastData, HourlyForecastData, DailyForecastData
except ImportError:
    # 구버전 호환성을 위한 더미 클래스
    WeeklyForecastData = None
    HourlyForecastData = None  
    DailyForecastData = None
from utils import parse_location_input, format_temperature, get_weather_emoji, format_timestamp
from storage import storage
from location_service import location_service, get_popular_cities

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_custom_style():
    """커스텀 스타일 적용"""
    st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 0.5rem 0;
        }
        .weather-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .forecast-item {
            text-align: center;
            padding: 10px;
            margin: 5px;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.05);
        }
        .stTab [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTab [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="🌤️ 고급 날씨 앱",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 스타일 적용
    apply_custom_style()
    
    # API 연결 확인
    try:
        weather_api = get_weather_api()
        st.sidebar.success("✅ API 연결 성공")
    except Exception as e:
        st.sidebar.error(f"❌ API 연결 실패: {e}")
        st.error("🔑 API 키가 설정되지 않았습니다!")
        return
    
    # 사이드바 구성
    setup_sidebar()
    
    # 메인 탭 구성
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 현재 날씨", "📅 주간 예보", "⏰ 시간별 예보", 
        "🌍 지역 비교", "⭐ 즐겨찾기", "📊 내 기록"
    ])
    
    with tab1:
        current_weather_tab()
    
    with tab2:
        weekly_forecast_tab()
    
    with tab3:
        hourly_forecast_tab()
        
    with tab4:
        location_comparison_tab()
        
    with tab5:
        favorites_tab()
        
    with tab6:
        saved_records_tab()

def setup_sidebar():
    """사이드바 설정"""
    st.sidebar.title("🌤️ 날씨 앱")
    
    # 위치 검색 섹션
    st.sidebar.header("📍 위치 선택")
    
    # 현재 위치 버튼
    if st.sidebar.button("📍 현재 위치 사용"):
        st.sidebar.info("브라우저에서 위치 접근을 허용해주세요.")
        location_service.render_location_component()
    
    # 위치 상태 표시
    if location_service.has_location():
        st.sidebar.success(location_service.format_location_string())
    elif location_service.get_location_error():
        st.sidebar.error(f"위치 오류: {location_service.get_location_error()}")
    
    # 도시 검색
    city_input = st.sidebar.text_input(
        "🔍 도시 검색",
        placeholder="예: Seoul, London, New York"
    )
    
    # 검색 히스토리
    history = storage.get_search_history(5)
    if history:
        st.sidebar.subheader("🕒 최근 검색")
        for item in history:
            if st.sidebar.button(f"🔄 {item.query}", key=f"history_{item.timestamp}"):
                st.session_state.selected_location = item.query
                st.experimental_rerun()
    
    # 인기 도시
    st.sidebar.subheader("🌟 인기 도시")
    popular_cities = get_popular_cities()
    
    selected_region = st.sidebar.selectbox(
        "지역 선택", 
        list(popular_cities.keys()),
        index=0
    )
    
    for city in popular_cities[selected_region]:
        if st.sidebar.button(f"{city['name']}", key=f"popular_{city['query']}"):
            st.session_state.selected_location = city['query']
            st.experimental_rerun()
    
    # 설정된 위치 저장
    if city_input:
        st.session_state.selected_location = city_input
    
    # 즐겨찾기 섹션
    favorites = storage.get_favorites()
    if favorites:
        st.sidebar.subheader("⭐ 즐겨찾기")
        for fav in favorites[:5]:  # 상위 5개만 표시
            if st.sidebar.button(f"⭐ {fav.name}", key=f"fav_{fav.query}"):
                st.session_state.selected_location = fav.query
                st.experimental_rerun()
    
    # 앱 정보
    st.sidebar.markdown("---")
    stats = storage.get_storage_stats()
    st.sidebar.markdown(f"""
    **📊 앱 통계**
    - 즐겨찾기: {stats['favorites_count']}개
    - 검색 기록: {stats['history_count']}개  
    - 저장된 기록: {stats['saved_weather_count']}개
    """)

def get_current_location():
    """현재 선택된 위치 가져오기"""
    # 현재 위치 우선
    if location_service.has_location():
        return location_service.get_location_query()
    
    # 세션에서 선택된 위치
    if 'selected_location' in st.session_state and st.session_state.selected_location:
        return parse_location_input(st.session_state.selected_location)
    
    # 기본값
    return parse_location_input("Seoul,KR")

def current_weather_tab():
    """현재 날씨 탭"""
    st.header("🏠 현재 날씨")
    
    location = get_current_location()
    if not location:
        st.info("👈 사이드바에서 위치를 선택해주세요.")
        return
    
    try:
        # 현재 날씨 가져오기
        weather_api = get_weather_api()
        weather = weather_api.get_current_weather(location)
        
        # 검색 히스토리에 추가
        if 'q' in location:
            storage.add_search_history(location['q'], True)
        
        # 현재 날씨 표시
        display_current_weather(weather)
        
        # 오늘의 예보 차트
        display_today_forecast_chart(weather)
        
        # 지도 표시
        display_weather_map(weather)
        
    except WeatherAPIError as e:
        st.error(f"❌ 날씨 정보를 가져올 수 없습니다: {e}")
        if 'q' in location:
            storage.add_search_history(location['q'], False)

def weekly_forecast_tab():
    """주간 예보 탭"""
    st.header("📅 주간 날씨 예보")
    
    location = get_current_location()
    if not location:
        st.info("👈 사이드바에서 위치를 선택해주세요.")
        return
    
    try:
        weather_api = get_weather_api()
        weekly_data = weather_api.get_weekly_forecast(location)
        
        # 주간 예보 표시
        display_weekly_forecast(weekly_data)
        
        # 주간 온도 트렌드 차트
        display_weekly_chart(weekly_data)
        
    except WeatherAPIError as e:
        st.error(f"❌ 주간 예보를 가져올 수 없습니다: {e}")
        # 대안으로 기본 5일 예보 표시
        try:
            forecast_data = weather_api.get_forecast(location)
            daily_forecast = weather_api.get_daily_forecast(location, days=5)
            st.warning("상세 주간 예보 대신 5일 예보를 표시합니다.")
            display_basic_forecast(daily_forecast)
        except Exception:
            pass

def hourly_forecast_tab():
    """시간별 예보 탭"""
    st.header("⏰ 시간별 날씨 예보")
    
    location = get_current_location()
    if not location:
        st.info("👈 사이드바에서 위치를 선택해주세요.")
        return
    
    # 시간 범위 선택
    hours_options = {"24시간": 24, "48시간": 48}
    selected_hours = st.selectbox(
        "예보 기간 선택",
        list(hours_options.keys())
    )
    
    try:
        weather_api = get_weather_api()
        hourly_data = weather_api.get_hourly_forecast(location, hours=hours_options[selected_hours])
        
        # 시간별 예보 표시
        display_hourly_forecast(hourly_data)
        
        # 시간별 차트
        display_hourly_chart(hourly_data)
        
    except WeatherAPIError as e:
        st.error(f"❌ 시간별 예보를 가져올 수 없습니다: {e}")
        # 대안으로 기본 예보 표시
        try:
            forecast_data = weather_api.get_forecast(location)
            st.warning("상세 시간별 예보 대신 3시간 간격 예보를 표시합니다.")
            display_basic_hourly_forecast(forecast_data)
        except Exception:
            pass

def location_comparison_tab():
    """지역 비교 탭"""
    st.header("🌍 지역별 날씨 비교")
    
    # 비교할 도시들 선택
    st.subheader("비교할 도시 선택")
    
    # 멀티셀렉트로 도시 선택
    popular_cities = get_popular_cities()
    all_cities = []
    for region, cities in popular_cities.items():
        all_cities.extend([f"{city['name']} ({city['query']})" for city in cities])
    
    selected_cities = st.multiselect(
        "도시 선택 (최대 5개)",
        all_cities,
        default=["서울 (Seoul,KR)", "도쿄 (Tokyo,JP)", "뉴욕 (New York,US)"],
        max_selections=5
    )
    
    if selected_cities:
        display_cities_comparison(selected_cities)

def favorites_tab():
    """즐겨찾기 탭"""
    st.header("⭐ 즐겨찾기 관리")
    
    # 즐겨찾기 추가
    st.subheader("새 즐겨찾기 추가")
    col1, col2 = st.columns(2)
    
    with col1:
        fav_name = st.text_input("이름", placeholder="예: 우리집")
    with col2:
        fav_query = st.text_input("위치", placeholder="예: Seoul,KR")
    
    if st.button("⭐ 즐겨찾기 추가"):
        if fav_name and fav_query:
            if storage.add_favorite(fav_name, fav_query):
                st.success(f"✅ '{fav_name}' 즐겨찾기에 추가됨!")
                st.experimental_rerun()
            else:
                st.warning("이미 즐겨찾기에 있는 위치입니다.")
        else:
            st.error("이름과 위치를 모두 입력해주세요.")
    
    # 즐겨찾기 목록
    st.subheader("즐겨찾기 목록")
    favorites = storage.get_favorites()
    
    if not favorites:
        st.info("아직 즐겨찾기가 없습니다.")
        return
    
    for fav in favorites:
        col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
        
        with col1:
            st.write(f"⭐ **{fav.name}**")
        with col2:
            st.write(f"📍 {fav.query}")
        with col3:
            if st.button("보기", key=f"view_{fav.query}"):
                st.session_state.selected_location = fav.query
                st.experimental_rerun()
        with col4:
            if st.button("삭제", key=f"delete_{fav.query}"):
                storage.remove_favorite(fav.query)
                st.success(f"'{fav.name}' 삭제됨!")
                st.experimental_rerun()

def saved_records_tab():
    """저장된 기록 탭"""
    st.header("📊 내 날씨 기록")
    
    # 현재 날씨 저장
    location = get_current_location()
    if location:
        st.subheader("현재 날씨 저장")
        
        note = st.text_input("메모 (선택사항)", placeholder="예: 산책하기 좋은 날씨")
        
        if st.button("💾 현재 날씨 저장"):
            try:
                weather_api = get_weather_api()
                weather = weather_api.get_current_weather(location)
                
                location_str = f"{weather.city}, {weather.country}"
                weather_data = {
                    'temperature': weather.temperature,
                    'weather_description': weather.weather_description,
                    'humidity': weather.humidity,
                    'wind_speed': weather.wind_speed,
                    'pressure': weather.pressure
                }
                
                storage.save_weather_record(location_str, weather_data, note)
                st.success("✅ 날씨 기록이 저장되었습니다!")
                st.experimental_rerun()
                
            except WeatherAPIError as e:
                st.error(f"❌ 날씨 정보를 가져올 수 없습니다: {e}")
    
    # 저장된 기록 표시
    st.subheader("저장된 기록")
    records = storage.get_saved_weather()
    
    if not records:
        st.info("아직 저장된 기록이 없습니다.")
        return
    
    for record in records:
        with st.expander(f"📅 {record.location} - {record.timestamp[:10]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**🌡️ 온도**: {record.weather_data['temperature']}°C")
                st.write(f"**🌤️ 날씨**: {record.weather_data['weather_description']}")
                st.write(f"**💧 습도**: {record.weather_data['humidity']}%")
            
            with col2:
                st.write(f"**💨 풍속**: {record.weather_data['wind_speed']} m/s")
                st.write(f"**🌬️ 기압**: {record.weather_data['pressure']} hPa")
                if record.user_note:
                    st.write(f"**📝 메모**: {record.user_note}")
            
            if st.button("🗑️ 삭제", key=f"del_record_{record.timestamp}"):
                storage.delete_weather_record(record.timestamp)
                st.success("기록이 삭제되었습니다!")
                st.experimental_rerun()

# 디스플레이 함수들
def display_current_weather(weather):
    """현재 날씨 표시"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌡️ 온도",
            value=f"{weather.temperature}°C",
            delta=f"체감 {weather.feels_like}°C"
        )
    
    with col2:
        st.metric(
            label="💧 습도",
            value=f"{weather.humidity}%"
        )
    
    with col3:
        st.metric(
            label="💨 풍속",
            value=f"{weather.wind_speed} m/s"
        )
    
    with col4:
        st.metric(
            label="🌬️ 기압",
            value=f"{weather.pressure} hPa"
        )
    
    # 날씨 설명과 아이콘
    st.markdown(f"""
    <div style='text-align: center; padding: 20px;'>
        <h2>{get_weather_emoji(weather.weather_main)} {weather.weather_description}</h2>
        <h3>📍 {weather.city}, {weather.country}</h3>
    </div>
    """, unsafe_allow_html=True)

def display_today_forecast_chart(weather):
    """오늘의 예보 차트 (간단한 버전)"""
    st.subheader("📊 오늘의 날씨 요약")
    
    # 간단한 게이지 차트
    fig = go.Figure()
    
    # 온도 게이지
    fig.add_trace(go.Indicator(
        mode = "gauge+number+delta",
        value = weather.temperature,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "현재 온도 (°C)"},
        delta = {'reference': 20},
        gauge = {
            'axis': {'range': [-20, 50]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-20, 0], 'color': "lightblue"},
                {'range': [0, 20], 'color': "yellow"},
                {'range': [20, 50], 'color': "orange"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 35
            }
        }
    ))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_weather_map(weather):
    """날씨 지도 표시"""
    st.subheader("🗺️ 위치")
    
    # 지도 데이터 준비
    map_data = pd.DataFrame({
        'lat': [weather.lat],
        'lon': [weather.lon],
        'location': [f"{weather.city}, {weather.country}"],
        'temperature': [weather.temperature]
    })
    
    st.map(map_data)

def display_weekly_forecast(weekly_data):
    """주간 예보 표시"""
    st.subheader("📅 7일간 날씨 예보")
    
    cols = st.columns(len(weekly_data.daily_forecasts))
    
    for i, day in enumerate(weekly_data.daily_forecasts):
        with cols[i]:
            date = datetime.fromtimestamp(day.timestamp)
            st.markdown(f"**{date.strftime('%m/%d')}**")
            st.markdown(f"**{date.strftime('%a')}**")
            st.markdown(f"🌡️ {day.temp_max:.1f}°")
            st.markdown(f"🌡️ {day.temp_min:.1f}°")
            st.markdown(f"{get_weather_emoji(day.weather_main)}")
            st.markdown(f"{day.weather_description}")

def display_weekly_chart(weekly_data):
    """주간 온도 트렌드 차트"""
    st.subheader("📈 주간 온도 트렌드")
    
    dates = []
    temp_max = []
    temp_min = []
    
    for day in weekly_data.daily_forecasts:
        dates.append(datetime.fromtimestamp(day.timestamp))
        temp_max.append(day.temp_max)
        temp_min.append(day.temp_min)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_max,
        mode='lines+markers',
        name='최고기온',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_min,
        mode='lines+markers',
        name='최저기온',
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        title="주간 온도 변화",
        xaxis_title="날짜",
        yaxis_title="온도 (°C)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_hourly_forecast(hourly_data):
    """시간별 예보 표시"""
    st.subheader("⏰ 시간별 날씨")
    
    # 테이블 형태로 표시
    data = []
    for hour in hourly_data[:12]:  # 처음 12시간만
        time_str = datetime.fromtimestamp(hour.timestamp).strftime('%H:%M')
        data.append({
            '시간': time_str,
            '온도': f"{hour.temperature:.1f}°C",
            '체감온도': f"{hour.feels_like:.1f}°C",
            '날씨': hour.weather_description,
            '습도': f"{hour.humidity}%",
            '풍속': f"{hour.wind_speed:.1f}m/s"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

def display_hourly_chart(hourly_data):
    """시간별 차트"""
    st.subheader("📊 시간별 온도 및 습도")
    
    times = [datetime.fromtimestamp(h.timestamp) for h in hourly_data]
    temps = [h.temperature for h in hourly_data]
    humidity = [h.humidity for h in hourly_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode='lines+markers',
        name='온도 (°C)',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=times, y=humidity,
        mode='lines+markers',
        name='습도 (%)',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="시간별 온도 및 습도 변화",
        xaxis_title="시간",
        yaxis=dict(title="온도 (°C)", side="left"),
        yaxis2=dict(title="습도 (%)", side="right", overlaying="y"),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_cities_comparison(selected_cities):
    """도시별 날씨 비교"""
    if not selected_cities:
        st.info("비교할 도시를 선택해주세요.")
        return
    
    st.subheader("🌍 선택된 도시들의 현재 날씨")
    
    # 도시별 날씨 정보 수집
    cities_data = []
    weather_api = get_weather_api()
    
    for city_str in selected_cities:
        try:
            # 도시명 추출 (예: "서울 (Seoul,KR)" -> "Seoul,KR")
            city_query = city_str.split('(')[1].replace(')', '')
            location = parse_location_input(city_query)
            weather = weather_api.get_current_weather(location)
            
            cities_data.append({
                '도시': weather.city,
                '국가': weather.country,
                '온도': weather.temperature,
                '체감온도': weather.feels_like,
                '날씨': weather.weather_description,
                '습도': weather.humidity,
                '풍속': weather.wind_speed,
                '기압': weather.pressure
            })
        except Exception as e:
            st.warning(f"{city_str} 날씨 정보를 가져올 수 없습니다: {e}")
    
    if cities_data:
        # 데이터프레임으로 표시
        df = pd.DataFrame(cities_data)
        st.dataframe(df, use_container_width=True)
        
        # 온도 비교 차트
        fig = px.bar(
            df, 
            x='도시', 
            y='온도',
            title="도시별 현재 온도 비교",
            color='온도',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_basic_forecast(daily_forecast):
    """기본 5일 예보 표시"""
    st.subheader("📅 5일 예보")
    
    cols = st.columns(len(daily_forecast))
    
    for i, day in enumerate(daily_forecast):
        with cols[i]:
            st.markdown(f"**{day['date'][5:]}**")  # MM-DD 형식
            st.markdown(f"🌡️ {day['temp_max']:.1f}°")
            st.markdown(f"🌡️ {day['temp_min']:.1f}°")
            st.markdown(f"💧 {day['humidity_avg']:.0f}%")
            st.markdown(f"{day['weather_description']}")

def display_basic_hourly_forecast(forecast_data):
    """기본 시간별 예보 표시 (3시간 간격)"""
    st.subheader("⏰ 3시간 간격 예보")
    
    data = []
    for forecast in forecast_data[:8]:  # 24시간 분량
        time_str = datetime.fromtimestamp(forecast.timestamp).strftime('%m/%d %H:%M')
        data.append({
            '시간': time_str,
            '온도': f"{forecast.temperature:.1f}°C",
            '날씨': forecast.weather_description,
            '습도': f"{forecast.humidity}%",
            '강수확률': f"{forecast.pop:.0f}%"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()