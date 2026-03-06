# oneOnOne 백엔드 API

Spring Boot 4.0 + Kotlin으로 구현된 oneOnOne 프로젝트의 백엔드 서버입니다.
Git 저장소 ZIP 파일을 업로드 받아 JGit으로 분석하고, 커밋 통계를 반환하는 REST API를 제공합니다.

## 기술 스택

- **Spring Boot**: 4.0.0
- **Kotlin**: 2.1.0
- **JGit**: 7.1.0 (Git 분석)
- **H2 Database**: 개발 환경
- **PostgreSQL**: 운영 환경 (선택)
- **Gradle**: 빌드 도구

## 프로젝트 구조

```
backend/
├── src/main/kotlin/com/oneonone/
│   ├── OneOnOneApplication.kt           # 메인 애플리케이션
│   ├── config/
│   │   └── WebConfig.kt                 # CORS 설정
│   ├── controller/
│   │   └── AnalysisController.kt        # POST /api/analyze
│   ├── service/
│   │   ├── GitAnalysisService.kt        # JGit 핵심 로직
│   │   ├── FileProcessingService.kt     # ZIP 처리
│   │   └── StatisticsService.kt         # 통계 계산
│   ├── domain/
│   │   ├── AnalysisResult.kt            # JPA Entity
│   │   └── CommitInfo.kt
│   ├── repository/
│   │   └── AnalysisResultRepository.kt
│   ├── dto/
│   │   └── AnalysisResponse.kt
│   └── exception/
│       └── GlobalExceptionHandler.kt
├── src/main/resources/
│   ├── application.yml
│   └── application-dev.yml
└── build.gradle.kts
```

## 요구사항

- **Java 21** 이상
- **Gradle** 8.x 이상 (Wrapper 포함)

## 설치 및 실행

### 1. Gradle 의존성 다운로드

```bash
cd backend
./gradlew clean build
```

### 2. 애플리케이션 실행

```bash
./gradlew bootRun
```

서버가 `http://localhost:8080`에서 실행됩니다.

### 3. 헬스체크

```bash
curl http://localhost:8080/api/health
```

응답:
```json
{"status": "OK"}
```

## API 명세

### POST /api/analyze

Git 저장소 ZIP 파일을 분석하여 커밋 통계를 반환합니다.

**요청:**

```bash
curl -X POST http://localhost:8080/api/analyze \
  -F "repositories=@project1.zip" \
  -F "repositories=@project2.zip" \
  -F "userName=your-name" \
  -F "quarter=Q1"
```

**요청 파라미터:**
- `repositories`: MultipartFile[] (ZIP 파일들)
- `userName`: String (Git 사용자 이름 또는 이메일)
- `quarter`: String (Q1, Q2, Q3, Q4)

**응답:**

```json
{
  "id": 1,
  "totalCommits": 42,
  "totalFiles": 128,
  "linesAdded": 3450,
  "linesDeleted": 890,
  "commitsByDate": {
    "2024-01-15": 5,
    "2024-01-16": 8,
    "2024-01-17": 3
  }
}
```

## 환경 설정

### application.yml

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 100MB
      max-request-size: 500MB

  datasource:
    url: jdbc:h2:mem:oneonone
    driver-class-name: org.h2.Driver

  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true

server:
  port: 8080
```

### H2 Console

개발 환경에서 H2 콘솔에 접속할 수 있습니다:

- URL: `http://localhost:8080/h2-console`
- JDBC URL: `jdbc:h2:mem:oneonone`
- Username: `sa`
- Password: (비어 있음)

## 프론트엔드 연동

프론트엔드는 `/Users/j6161990/Documents/GitHub/claude-lab/docs/`에 위치합니다.

프론트엔드 실행:

```bash
cd ../docs
python -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 열고, API URL에 `http://localhost:8080`을 입력하세요.

## 주요 기능

### 1. ZIP 파일 처리 (FileProcessingService)
- ZIP 파일 압축 해제
- 임시 디렉토리 자동 정리

### 2. Git 분석 (GitAnalysisService)
- JGit을 사용한 Git 저장소 열기
- 사용자 이름/이메일 필터링
- 분기별 날짜 범위 필터링
- 커밋별 Diff 분석 (라인 추가/삭제)

### 3. 통계 계산 (StatisticsService)
- 총 커밋 수, 파일 변경 수
- 라인 추가/삭제 통계
- 날짜별 커밋 수 집계 (차트용)

## 개발

### 테스트 실행

```bash
./gradlew test
```

### 빌드 (JAR 파일 생성)

```bash
./gradlew build
```

생성된 JAR: `build/libs/oneonone-backend-0.0.1-SNAPSHOT.jar`

### 실행 (JAR)

```bash
java -jar build/libs/oneonone-backend-0.0.1-SNAPSHOT.jar
```

## 문제 해결

### 1. gradlew 실행 권한 오류

```bash
chmod +x gradlew
```

### 2. Java 버전 오류

Java 21 이상이 설치되어 있는지 확인:

```bash
java -version
```

SDKMAN 사용 시:

```bash
sdk install java 21.0.1-tem
sdk use java 21.0.1-tem
```

### 3. 파일 업로드 크기 제한 오류

`application.yml`에서 `max-file-size`를 조정하세요.

## 다음 단계

- [ ] POST /api/generate/{type} API 구현 (문서 생성)
- [ ] AI 연동 (Claude API 또는 GPT API)
- [ ] 비동기 처리 (대용량 저장소)
- [ ] Docker 컨테이너화
- [ ] 배포 (Heroku, Railway, Google Cloud Run)

## Context7 활용

이 프로젝트는 Context7 MCP 서버를 사용하여 최신 Spring Boot 4.0 및 Kotlin 문서를 참조하여 개발되었습니다.

## 라이선스

MIT License
