# OneOnOne 회고 도구

Git 저장소 ZIP 파일을 업로드하면 분기별 커밋 통계를 즉시 반환합니다.
Jira 이메일을 입력하면 Jira/Confluence 데이터도 함께 반환됩니다.

## 구조

```
OneOnOne/
├── backend/   # Kotlin Spring Boot (DB 없음, 즉시 반환)
└── frontend/  # Next.js (sessionStorage 기반)
```

## 백엔드 실행

```bash
cd backend
./gradlew bootRun
```

Jira 연동이 필요하면 `.env.example`을 참고하여 환경변수를 설정하세요.

## 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

## API

### POST /api/analyze

multipart/form-data:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| repositories | File[] | O | Git 저장소 ZIP 파일 |
| userName | String | O | Git 작성자 이름 또는 이메일 |
| quarter | String | O | Q1~Q4 |
| jiraEmail | String | - | 입력 시 Jira 데이터 포함 |

### GET /api/health

```json
{ "status": "OK" }
```
