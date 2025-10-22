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
├── app.py                    # Streamlit 메인 애플리케이션
├── api.py                    # OpenWeather API 클라이언트
├── utils.py                  # 유틸리티 함수들
├── config.py                 # 설정 및 환경변수
├── requirements.txt          # Python 의존성
├── packages.txt              # 시스템 패키지 (Streamlit Cloud용)
├── .env.example              # 환경변수 템플릿
├── .gitignore               # Git 무시 파일 목록
├── .streamlit/
│   ├── config.toml          # Streamlit 설정
│   └── secrets.toml         # 배포용 환경변수 템플릿
├── tests/
│   └── test_weather_app.py  # 유닛 테스트
└── README.md                # 프로젝트 문서
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **API**: OpenWeather API
- **시각화**: Plotly
- **데이터 처리**: Pandas
- **HTTP 클라이언트**: Requests

## 🌐 배포

### Streamlit Cloud 배포 (권장)

1. **GitHub 저장소 준비**
   ```bash
   git add .
   git commit -m "Add weather app"
   git push origin main
   ```

2. **Streamlit Cloud 배포**
   - [Streamlit Cloud](https://share.streamlit.io/)에 로그인
   - "New app" → "From existing repo" 선택
   - 저장소 URL 입력: `https://github.com/yuniskim-coder/testdata`
   - Main file path: `app.py`
   - Branch: `main`

3. **환경변수(Secrets) 설정**
   
   배포 후 앱 설정에서 **Secrets** 탭에 다음 내용을 추가:
   ```toml
   [api]
   openweather_key = "f4e5ad99faddf91dce8add9f4ec8723f"

   [app]
   default_city = "Seoul"
   default_country = "KR" 
   cache_ttl_seconds = 600
   ```

4. **배포 완료**
   - 자동으로 빌드 및 배포됩니다
   - 공유 가능한 URL이 생성됩니다 (예: `https://your-app-name.streamlit.app`)

### 로컬 실행

```bash
# 환경 설정
pip install -r requirements.txt

# .env 파일 생성
cp .env.example .env
# .env에서 API 키 설정

# 앱 실행
streamlit run app.py
```

### 배포된 앱 특징

- ✅ **자동 HTTPS**: 보안 연결
- ✅ **무료 호스팅**: Streamlit Cloud 무료 플랜
- ✅ **자동 업데이트**: GitHub push 시 자동 재배포
- ✅ **커스텀 도메인**: 설정 가능 (Pro 플랜)
- ✅ **환경변수 관리**: Secrets로 안전한 API 키 관리

### Docker 배포 (선택사항)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Docker 이미지 빌드
docker build -t weather-app .

# 컨테이너 실행
docker run -p 8501:8501 -e OPENWEATHER_API_KEY=your_key weather-app
```

---

**Made with ❤️ using Streamlit and OpenWeather API**