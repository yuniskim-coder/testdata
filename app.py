"""
Streamlit Weather App - 날씨 정보를 시각화하는 웹 애플리케이션
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time

from api import weather_api, WeatherAPIError
from utils import (
    parse_location_input, 
    format_temperature, 
    format_wind_speed, 
    format_datetime,
    get_weather_emoji,
    create_cache_key,
    cached_weather_request
)
from config import (
    TEMPERATURE_UNITS, 
    DEFAULT_CITY, 
    DEFAULT_COUNTRY,
    OPENWEATHER_ICON_URL
)

# Page configuration
st.set_page_config(
    page_title="날씨 정보 앱",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .weather-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .forecast-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #74b9ff;
    }
    .temperature-high {
        color: #e74c3c;
        font-weight: bold;
    }
    .temperature-low {
        color: #3498db;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Header
    st.title("🌤️ 날씨 정보 앱")
    st.markdown("**OpenWeather API**를 사용하여 실시간 날씨 정보와 예보를 제공합니다.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # Location input
        st.subheader("📍 위치 설정")
        location_type = st.radio(
            "위치 입력 방식",
            ["도시명", "좌표"],
            help="도시명을 입력하거나 위도/경도 좌표를 사용할 수 있습니다."
        )
        
        if location_type == "도시명":
            location_input = st.text_input(
                "도시명을 입력하세요",
                value=f"{DEFAULT_CITY},{DEFAULT_COUNTRY}",
                placeholder="예: Seoul,KR 또는 Seoul",
                help="도시명만 입력하거나 '도시명,국가코드' 형식으로 입력하세요."
            )
        else:
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("위도", value=37.5665, format="%.4f", help="위도 (-90 ~ 90)")
            with col2:
                lon = st.number_input("경도", value=126.9780, format="%.4f", help="경도 (-180 ~ 180)")
            location_input = f"{lat},{lon}"
        
        # Units selection
        st.subheader("🌡️ 단위 설정")
        units = st.selectbox(
            "온도 단위",
            options=list(TEMPERATURE_UNITS.keys()),
            format_func=lambda x: TEMPERATURE_UNITS[x]["name"],
            index=0
        )
        
        # Forecast days
        forecast_days = st.slider("예보 일수", min_value=1, max_value=5, value=3)
        
        # Refresh button
        if st.button("🔄 새로고침", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Main content
    if location_input:
        try:
            # Parse location
            location_params = parse_location_input(location_input)
            
            # Show loading spinner
            with st.spinner("날씨 정보를 가져오는 중..."):
                # Create cache keys
                current_cache_key = create_cache_key(location_params, units, "current")
                forecast_cache_key = create_cache_key(location_params, units, "forecast")
                
                # Get current weather with error handling
                try:
                    current_weather = weather_api.get_current_weather(location_params, units)
                except Exception as e:
                    st.error(f"현재 날씨 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")
                    return
                
                # Get forecast with error handling
                try:
                    daily_forecast = weather_api.get_daily_forecast(location_params, units, forecast_days)
                except Exception as e:
                    st.error(f"예보 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")
                    # Continue with current weather only
                    daily_forecast = []
            
            # Display current weather
            display_current_weather(current_weather, units)
            
            # Display forecast if available
            if daily_forecast:
                display_forecast(daily_forecast, units)
                display_charts(daily_forecast, units)
            
            # Display map
            display_map(current_weather)
            
        except ValueError as e:
            st.error(f"❌ 입력 오류: {str(e)}")
        except WeatherAPIError as e:
            st.error(f"🌐 API 오류: {str(e)}")
        except Exception as e:
            st.error(f"💥 예상치 못한 오류가 발생했습니다: {str(e)}")
            st.info("문제가 지속되면 새로고침을 시도해보세요.")
            # Show debug info in development
            if st.checkbox("디버그 정보 표시"):
                st.exception(e)


def display_current_weather(weather, units):
    """Display current weather information"""
    
    st.header("🌍 현재 날씨")
    
    # Main weather card
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="weather-card">
            <h2>{weather.city}, {weather.country}</h2>
            <h1>{format_temperature(weather.temperature, units)}</h1>
            <p style="font-size: 1.2em; margin: 0;">
                {get_weather_emoji(weather.weather_main, 0)} {weather.weather_description}
            </p>
            <p style="margin: 0.5rem 0;">
                체감온도: {format_temperature(weather.feels_like, units)}
            </p>
            <small>{format_datetime(weather.timestamp, weather.timezone_offset)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Weather icon
        icon_url = OPENWEATHER_ICON_URL.format(icon=weather.weather_icon)
        st.image(icon_url, width=150)
    
    # Weather metrics
    st.subheader("📊 상세 정보")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💧 습도",
            value=f"{weather.humidity}%"
        )
    
    with col2:
        st.metric(
            label="🌪️ 풍속",
            value=format_wind_speed(weather.wind_speed, units)
        )
    
    with col3:
        st.metric(
            label="🗜️ 기압",
            value=f"{weather.pressure} hPa"
        )
    
    with col4:
        if weather.visibility:
            visibility_km = weather.visibility / 1000
            st.metric(
                label="👁️ 가시거리",
                value=f"{visibility_km:.1f} km"
            )


def display_forecast(forecast_data, units):
    """Display daily forecast"""
    
    st.header("📅 일기예보")
    
    cols = st.columns(len(forecast_data))
    
    for i, day_data in enumerate(forecast_data):
        with cols[i]:
            date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%m/%d')
            weekday = date_obj.strftime('%a')
            
            # Weather icon
            icon_url = OPENWEATHER_ICON_URL.format(icon=day_data['weather_icon'])
            st.image(icon_url, width=80)
            
            st.markdown(f"""
            <div class="forecast-card">
                <h4>{day_name}</h4>
                <p style="margin: 0; color: #666;">{weekday}</p>
                <p style="margin: 0.5rem 0;">
                    <span class="temperature-high">{format_temperature(day_data['temp_max'], units)}</span>
                    /
                    <span class="temperature-low">{format_temperature(day_data['temp_min'], units)}</span>
                </p>
                <small style="color: #888;">{day_data['weather_description']}</small>
                <br>
                <small style="color: #0984e3;">💧 {day_data['pop_max']:.0f}%</small>
            </div>
            """, unsafe_allow_html=True)


def display_charts(forecast_data, units):
    """Display weather charts"""
    
    if not forecast_data:
        st.info("차트를 표시할 예보 데이터가 없습니다.")
        return
    
    st.header("📈 날씨 차트")
    
    try:
        # Prepare data for charts
        dates = [datetime.strptime(day['date'], '%Y-%m-%d') for day in forecast_data]
        temp_max = [day['temp_max'] for day in forecast_data]
        temp_min = [day['temp_min'] for day in forecast_data]
        humidity = [day['humidity_avg'] for day in forecast_data]
        pop = [day['pop_max'] for day in forecast_data]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature chart
            fig_temp = go.Figure()
            
            fig_temp.add_trace(go.Scatter(
                x=dates,
                y=temp_max,
                mode='lines+markers',
                name='최고기온',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8)
            ))
            
            fig_temp.add_trace(go.Scatter(
                x=dates,
                y=temp_min,
                mode='lines+markers',
                name='최저기온',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
            
            fig_temp.update_layout(
                title="기온 변화",
                xaxis_title="날짜",
                yaxis_title=f"온도 ({TEMPERATURE_UNITS[units]['symbol']})",
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Humidity and precipitation chart
            fig_humid = go.Figure()
            
            fig_humid.add_trace(go.Bar(
                x=dates,
                y=humidity,
                name='습도 (%)',
                marker_color='#74b9ff',
                yaxis='y'
            ))
            
            fig_humid.add_trace(go.Scatter(
                x=dates,
                y=pop,
                mode='lines+markers',
                name='강수확률 (%)',
                line=dict(color='#00b894', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            fig_humid.update_layout(
                title="습도 & 강수확률",
                xaxis_title="날짜",
                yaxis=dict(title="습도 (%)", side="left"),
                yaxis2=dict(title="강수확률 (%)", side="right", overlaying="y"),
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig_humid, use_container_width=True)
            
    except Exception as e:
        st.error(f"차트를 생성하는 중 오류가 발생했습니다: {str(e)}")
        st.info("차트 대신 텍스트로 예보 정보를 표시합니다.")
        
        # Fallback: display data as text
        for day in forecast_data:
            st.write(f"**{day['date']}**: 최고 {day['temp_max']:.1f}°, 최저 {day['temp_min']:.1f}°, 습도 {day['humidity_avg']:.0f}%, 강수확률 {day['pop_max']:.0f}%")


def display_map(weather):
    """Display location on map"""
    
    st.header("🗺️ 위치")
    
    # Create DataFrame for map
    map_data = pd.DataFrame({
        'lat': [weather.lat],
        'lon': [weather.lon]
    })
    
    st.map(map_data, zoom=10)
    
    # Show coordinates
    st.info(f"📍 좌표: {weather.lat:.4f}, {weather.lon:.4f}")


if __name__ == "__main__":
    main()