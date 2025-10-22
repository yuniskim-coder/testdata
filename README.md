# 🌤️ 날씨 정보 앱

OpenWeather API를 사용하여 실시간 날씨 정보와 예보를 제공하는 Streamlit 기반 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🌍 **실시간 날씨 정보**: 현재 기온, 체감온도, 습도, 풍속, 기압 등
- 📅 **5일 일기예보**: 최고/최저 기온, 강수확률, 날씨 상태
- 📊 **시각화 차트**: 기온 변화, 습도, 강수확률 그래프
- 🗺️ **지도 표시**: 검색한 위치를 지도에서 확인
- 🌡️ **단위 변환**: 섭씨/화씨/켈빈 온도 단위 선택
- 🔍 **다양한 검색 방식**: 도시명 또는 위도/경도 좌표 입력

## 🚀 시작하기

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd testdata

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

1. [OpenWeatherMap](https://openweathermap.org/api)에서 무료 API 키를 발급받으세요.
2. `.env.example` 파일을 복사하여 `.env` 파일을 생성하세요:

```bash
cp .env.example .env
```

3. `.env` 파일에서 API 키를 설정하세요:

```env
OPENWEATHER_API_KEY=f4e5ad99faddf91dce8add9f4ec8723f
DEFAULT_CITY=Seoul
DEFAULT_COUNTRY=KR
CACHE_TTL_SECONDS=600
```

### 3. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 앱을 사용할 수 있습니다.

## 📱 사용법

### 위치 검색
- **도시명**: `Seoul`, `Seoul,KR`, `New York,US` 형식으로 입력
- **좌표**: 위도/경도를 직접 입력 (예: 37.5665, 126.9780)

### 설정 옵션
- **온도 단위**: 섭씨(°C), 화씨(°F), 켈빈(K) 선택
- **예보 일수**: 1-5일 예보 기간 선택
- **자동 새로고침**: 캐시된 데이터를 새로 불러오기

## 🏗️ 프로젝트 구조

```
testdata/
├── app.py              # Streamlit 메인 애플리케이션
├── api.py              # OpenWeather API 클라이언트
├── utils.py            # 유틸리티 함수들
├── config.py           # 설정 및 환경변수
├── requirements.txt    # Python 의존성
├── .env.example        # 환경변수 템플릿
├── .gitignore         # Git 무시 파일 목록
└── README.md          # 프로젝트 문서
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **API**: OpenWeather API
- **시각화**: Plotly
- **데이터 처리**: Pandas
- **HTTP 클라이언트**: Requests

---

**Made with ❤️ using Streamlit and OpenWeather API**