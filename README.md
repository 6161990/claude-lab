# 원온원(OneOnOne) - 개발자 작업 회고 생성기

> Git 저장소를 분석하여 분기별 회고, 이력서, 피드백을 자동으로 생성해주는 AI 기반 도구

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Web-green.svg)
![Status](https://img.shields.io/badge/status-In%20Development-yellow.svg)

## 📖 프로젝트 소개

**원온원(OneOnOne)**은 개발자들이 분기마다 작성해야 하는 회고와 이력서를 자동화하는 웹 애플리케이션입니다.

여러 개의 Git 저장소를 업로드하면, AI가 당신의 커밋 히스토리를 분석하여:
- 📝 **분기별 회고 문서** 자동 생성
- 💼 **이력서용 프로젝트 설명** 작성
- 💡 **성장 피드백 및 개선 제안** 제공

## ✨ 주요 기능

### 1. 다중 저장소 분석
- 여러 Git 저장소(ZIP 파일)를 한 번에 업로드
- 사용자 이름 기반 필터링으로 본인의 기여만 추출
- 분기별(Q1-Q4) 또는 사용자 지정 기간 설정

### 2. 시각화된 통계
- 📊 커밋 수, 변경 파일 수, 코드 라인 통계
- 📈 시간별 커밋 활동 차트
- 🎯 작업 패턴 분석

### 3. AI 기반 문서 생성
- **회고 문서**: 주요 성과, 배운 점, 개선점 자동 작성
- **이력서 설명**: 프로젝트 경험을 정량화된 성과로 변환
- **피드백**: 코드 품질, 작업 패턴 기반 성장 제안

## 🛠️ 기술 스택

### Frontend (GitHub Pages)
- HTML5, JavaScript (ES6+)
- Tailwind CSS (스타일링)
- Chart.js (데이터 시각화)

### Backend (별도 배포)
- Spring Boot 3.x
- Kotlin
- JGit (Git 저장소 분석)
- PostgreSQL / SQLite

### AI
- Claude API 또는 GPT API

## 📦 설치 및 실행

### 프론트엔드 (GitHub Pages)

1. **저장소 클론**
```bash
git clone https://github.com/your-username/oneonone.git
cd oneonone
```

2. **로컬 테스트**
```bash
# Python 간이 서버 실행
cd docs
python -m http.server 8000

# 브라우저에서 http://localhost:8000 접속
```

3. **GitHub Pages 배포**
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) 참고

### 백엔드 (Spring Boot)

```bash
# 백엔드 디렉토리로 이동 (추후 구현)
cd backend

# Gradle 빌드
./gradlew build

# 실행
./gradlew bootRun
```

## 🚀 사용 방법

### 1단계: 저장소 준비
```bash
# Git 저장소를 ZIP으로 압축
zip -r project1.zip /path/to/project1/.git
zip -r project2.zip /path/to/project2/.git
```

### 2단계: 웹사이트 접속
- GitHub Pages URL: `https://your-username.github.io/oneonone/`

### 3단계: 정보 입력
1. 백엔드 API URL 입력 (예: `https://your-api.herokuapp.com`)
2. Git 사용자 이름 입력 (커밋에 사용한 이름 또는 이메일)
3. 분석 기간 선택 (Q1, Q2, Q3, Q4)

### 4단계: 저장소 업로드
- ZIP 파일을 드래그 앤 드롭 또는 파일 선택
- 여러 개의 저장소를 한 번에 업로드 가능

### 5단계: 분석 및 문서 생성
- **분석 시작** 버튼 클릭
- 통계 확인 후 원하는 문서 타입 선택:
  - 회고 생성
  - 이력서 생성
  - 피드백 받기

## 📂 프로젝트 구조

```
claude-lab/
├── docs/                        # GitHub Pages 프론트엔드
│   ├── index.html              # 메인 페이지
│   ├── css/
│   │   └── styles.css          # 커스텀 스타일
│   ├── js/
│   │   ├── upload.js           # 파일 업로드 처리
│   │   ├── analysis.js         # 분석 결과 표시
│   │   └── document.js         # 문서 생성 UI
│   └── images/                 # 이미지 리소스
├── backend/                     # Spring Boot 백엔드 (개발 예정)
├── workshop/                    # Cursor Rules 14-step 워크샵
├── RoadMap.md                   # 개발 로드맵
├── GITHUB_PAGES_DEPLOY.md       # 배포 가이드
└── README.md                    # 이 파일
```

## 🗺️ 개발 로드맵

자세한 개발 계획은 [RoadMap.md](RoadMap.md)를 참고하세요.

- [x] Phase 1: 프로젝트 설계 및 요구사항 정의
- [x] Phase 2: 프론트엔드 UI 개발 (GitHub Pages)
- [ ] Phase 3: 백엔드 API 개발 (Spring Boot + Kotlin)
- [ ] Phase 4: Git 분석 엔진 구현 (JGit)
- [ ] Phase 5: AI 연동 및 문서 생성
- [ ] Phase 6: 배포 및 테스트

## 🤝 기여하기

이 프로젝트는 학습 및 포트폴리오 목적으로 개발되었습니다. 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m '새로운 기능 추가'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참고하세요.

## 📚 관련 문서

- [개발 로드맵](RoadMap.md) - 상세한 개발 계획
- [GitHub Pages 배포 가이드](GITHUB_PAGES_DEPLOY.md) - 배포 방법
- [Cursor Rules 14-step](./workshop/Cursor_Rules_14steps/) - AI 기반 개발 프레임워크

## 💬 문의 및 지원

- Issues: [GitHub Issues](https://github.com/your-username/oneonone/issues)
- Email: your-email@example.com

---

**Made with ❤️ using Claude Code and Cursor**

이 프로젝트는 [Cursor Rules 14-step 프레임워크](./workshop/Cursor_Rules_14steps/)를 활용하여 개발되었습니다.
