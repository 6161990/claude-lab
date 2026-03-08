# OneOnOne - 개발자 회고 보고서 생성기

> Git 저장소를 업로드하면 AI가 커밋 이력과 소스코드를 분석하여 개발자 회고 보고서를 자동으로 작성해주는 웹 애플리케이션

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Web-green.svg)
![Status](https://img.shields.io/badge/status-In%20Development-yellow.svg)

## 프로젝트 소개

**OneOnOne**은 1:1 미팅이나 분기 회고를 위한 개발자 보고서를 자동으로 생성하는 도구입니다.

로컬 Git 저장소를 ZIP으로 압축하여 업로드하면, AI가 커밋 이력과 전체 소스코드를 분석하여 다음을 제공합니다:

- 이번 분기 핵심 기여 요약
- 이력서용 bullet point 성과
- 업무 & 코드 작성 성향 분석
- 코드 개선 포인트
- 성장 피드백

## 주요 기능

### 다중 저장소 분석
- ZIP 파일 최대 3개 동시 업로드 (파일당 최대 500MB)
- Git 이름 또는 이메일로 기여자 필터링
- 분석 기간 자유 설정 (기본값: 현재 분기)
- 커밋이 없는 기여자는 즉시 안내 메시지 반환

### Jira / Confluence 연동 (선택)
- Jira 이메일 입력 시 완료/진행 중 이슈 자동 포함
- Confluence 기여 페이지 분석에 반영

### 커스텀 프롬프트
- 분석 요청에 추가 지시사항 입력 가능
- 예: "1:1 미팅 관점에서 성장 포인트를 중심으로 분석해주세요"

## 기술 스택

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- shadcn/ui + Tailwind CSS

### Backend
- Spring Boot 3.4.1
- Kotlin 2.1.0
- JGit (Git 저장소 분석)
- Spring Web (REST API)

### AI
- Claude API (`claude-sonnet-4-6`)
- 최대 8,192 토큰 출력

## 프로젝트 구조

```
claude-lab/
├── OneOnOne/
│   ├── backend/                          # Spring Boot 백엔드
│   │   └── src/main/kotlin/com/oneonone/
│   │       ├── controller/               # REST API 컨트롤러
│   │       ├── service/
│   │       │   ├── ClaudeService.kt      # Claude API 호출 및 프롬프트 관리
│   │       │   ├── GitAnalysisService.kt # JGit 기반 저장소 분석
│   │       │   └── JiraService.kt        # Jira/Confluence 연동
│   │       ├── dto/                      # 요청/응답 데이터 클래스
│   │       └── config/                   # CORS, Jira 설정
│   └── frontend/                         # Next.js 프론트엔드
│       ├── app/
│       │   ├── page.tsx                  # 메인 업로드 폼
│       │   └── results/                  # 분析 결과 페이지
│       ├── components/ui/                # shadcn/ui 컴포넌트
│       └── lib/
│           ├── api-client.ts             # fetch 래퍼
│           └── types.ts                  # 공용 타입 정의
├── references/                           # 14단계 개발 프레임워크 문서
└── README.md
```

## 로컬 실행 방법

### 사전 준비
- JDK 21+
- Node.js 18+
- Anthropic API 키

### 백엔드

```bash
cd OneOnOne/backend

# 환경변수 설정
export ANTHROPIC_API_KEY=sk-ant-...

# 실행 (포트 8080)
./gradlew bootRun
```

Jira 연동을 원할 경우 추가로 설정:
```bash
export JIRA_BASE_URL=https://your-org.atlassian.net
export JIRA_EMAIL=service-account@company.com
export JIRA_API_TOKEN=your-token
export JIRA_ENABLED=true
```

### 프론트엔드

```bash
cd OneOnOne/frontend

npm install

# 백엔드 URL 설정 (기본값: http://localhost:8080)
echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local

npm run dev
# http://localhost:3000 접속
```

## 사용 방법

### 1단계: 저장소 ZIP 준비

GitHub의 "Download ZIP"은 커밋 이력이 없어 분析 불가합니다. 반드시 로컬에서 직접 압축하세요.

```bash
cd /path/to/your/project
zip -r repo.zip . --exclude "*/node_modules/*" "*/build/*" "*/.next/*" "*/.gradle/*"
```

### 2단계: 정보 입력

| 항목 | 필수 | 설명 |
|------|------|------|
| ZIP 파일 | 필수 | 저장소 ZIP (최대 3개, 각 500MB) |
| Git 이름/이메일 | 필수 | `git log`에 표시되는 author |
| 분析 기간 | 필수 | 시작일 ~ 종료일 |
| Jira 이메일 | 선택 | 입력 시 Jira/Confluence 데이터 포함 |
| 추가 분析 요청 | 선택 | 커스텀 프롬프트 |

### 3단계: 분析 시작

**분析 시작 →** 버튼 클릭 후 결과 페이지에서 보고서 확인

## API

### POST /api/analyze

```
Content-Type: multipart/form-data

repositories: File[]   # ZIP 파일 (1~3개)
userName:     string   # Git author 이름 또는 이메일
startDate:    string   # YYYY-MM-DD
endDate:      string   # YYYY-MM-DD
jiraEmail:    string?  # (선택) Jira 계정 이메일
customPrompt: string?  # (선택) 추가 분析 요청
```

응답:
```json
{
  "userName": "홍길동",
  "startDate": "2025-01-01",
  "endDate": "2025-03-31",
  "analysis": "## 1. 이번 분기 핵심 기여\n...",
  "jira": { ... }
}
```

### GET /api/health

서버 상태 확인

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `ANTHROPIC_API_KEY` | - | Claude API 키 (필수) |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | 사용할 Claude 모델 |
| `JIRA_BASE_URL` | - | Jira 도메인 |
| `JIRA_EMAIL` | - | Jira 서비스 계정 이메일 |
| `JIRA_API_TOKEN` | - | Jira API 토큰 |
| `JIRA_ENABLED` | `false` | Jira 연동 활성화 여부 |

## 라이선스

MIT License

---

**Made with Claude Code**
