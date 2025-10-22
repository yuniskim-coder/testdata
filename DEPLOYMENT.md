# 🚀 Streamlit Cloud 배포 체크리스트

## 배포 전 확인사항

### ✅ 필수 파일들
- [ ] `app.py` - 메인 애플리케이션 파일
- [ ] `requirements.txt` - Python 패키지 의존성 (고정 버전)
- [ ] `runtime.txt` - Python 버전 지정 (python-3.11)
- [ ] `.streamlit/config.toml` - Streamlit 설정
- [ ] `.streamlit/secrets.toml` - 환경변수 템플릿
- [ ] `README.md` - 프로젝트 문서

### ✅ 코드 검증
- [ ] 모든 import 구문이 올바른지 확인
- [ ] API 키가 하드코딩되지 않았는지 확인
- [ ] 로컬에서 정상 실행되는지 테스트
- [ ] 에러 처리가 적절한지 확인

### ✅ Git 저장소 준비
```bash
# 모든 변경사항 추가
git add .

# 커밋 메시지 작성
git commit -m "Prepare for Streamlit Cloud deployment"

# GitHub에 푸시
git push origin main
```

## 🌐 Streamlit Cloud 배포 단계

### 1. Streamlit Cloud 접속
- https://share.streamlit.io/ 로 이동
- GitHub 계정으로 로그인

### 2. 새 앱 생성
- "New app" 클릭
- "From existing repo" 선택
- Repository: `yuniskim-coder/testdata`
- Branch: `main`
- Main file path: `app.py`

## 🔧 배포 문제 해결

### installer returned a non-zero exit code 오류
이 오류가 발생한 경우:

1. **requirements.txt 최적화 완료**
   ```txt
   streamlit
   requests
   python-dotenv
   pandas
   plotly
   ```

2. **재배포 방법**
   - GitHub에 변경사항 푸시
   - Streamlit Cloud에서 "Reboot app" 클릭
   - 또는 앱 삭제 후 다시 배포

3. **대안 방법 (문제 지속시)**
   ```txt
   # 더 안정적인 최소 버전
   streamlit==1.25.0
   requests==2.28.0
   pandas==1.5.0
   plotly==5.10.0
   ```

### 3. Secrets 설정 (선택사항 - 이미 기본값 포함됨!)

**📌 중요**: 이제 API 키가 코드에 기본값으로 포함되어 있어서 별도 설정 없이도 바로 작동합니다!

선택적으로 Secrets에서 다른 API 키를 사용하려면:

```toml
[api]
openweather_key = "your_different_api_key_here"

[app]
default_city = "Seoul"
default_country = "KR"
cache_ttl_seconds = 600
```

### 4. 배포 완료
- 자동 빌드 및 배포 진행
- 완료 후 공유 URL 생성 (예: https://weather-app-name.streamlit.app)

## 🔧 배포 후 확인사항

### ✅ 기능 테스트
- [ ] 앱이 정상적으로 로드되는지 확인
- [ ] 날씨 검색이 작동하는지 테스트
- [ ] 차트와 지도가 표시되는지 확인
- [ ] 에러 처리가 올바르게 작동하는지 확인

### ✅ 성능 확인
- [ ] 페이지 로딩 속도 체크
- [ ] API 응답 시간 확인
- [ ] 캐싱이 작동하는지 검증

## 🚨 문제 해결

### 일반적인 배포 오류

1. **ModuleNotFoundError**
   - `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
   - 패키지 버전이 호환되는지 확인

2. **API 키 오류**
   - Secrets에 올바른 형식으로 API 키가 설정되어 있는지 확인
   - 키 이름이 코드와 일치하는지 확인

3. **Runtime 오류**
   - `runtime.txt`에 지원되는 Python 버전이 명시되어 있는지 확인
   - Streamlit Cloud에서 지원하는 Python 버전 확인

### 배포 로그 확인
- Streamlit Cloud 대시보드에서 "Manage app" → "Logs" 확인
- 실시간 에러 및 경고 메시지 모니터링

## 📱 배포 완료 후

### 공유하기
- 생성된 URL을 복사하여 공유
- QR 코드 생성 가능
- 소셜 미디어 공유 기능 활용

### 업데이트하기
- GitHub에 새 코드 푸시 시 자동 재배포
- 수동 재배포: "Reboot app" 버튼 클릭

---

**🎉 배포 준비 완료!** 

### ✅ 최종 상태 확인
- **로컬 테스트 성공**: Seoul 12.76°C 맑음 - 모든 기능 정상 작동 ✅
- **API 키 설정**: 코드에 내장되어 즉시 작동 가능 ✅  
- **배포 파일 완비**: requirements.txt, config.toml, .gitignore 등 모두 준비됨 ✅
- **강화된 구성**: 다중 설정 소스와 상세한 디버깅 정보 포함 ✅

**GitHub에 업로드 후 Streamlit Cloud에서 바로 배포하세요!**