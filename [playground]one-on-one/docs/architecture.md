# 원온원(1:1) 회고 생성 시스템 아키텍처

> 개발자의 Git 커밋 이력과 Jira/Confluence 데이터를 분석하여 분기별 회고를 자동 생성하는 시스템

---

## 1. 전체 시스템 아키텍처 (C4 Context)

```mermaid
graph TB
    User["개발자 (사용자)"]

    subgraph Frontend["프론트엔드 (포트 3000)"]
        HTML["HTML + Tailwind CSS"]
        JS_Upload["upload.js - ZIP 업로드"]
        JS_Analysis["analysis.js - 분석 결과 시각화"]
        JS_Doc["document.js - 문서 생성"]
        ChartJS["Chart.js - 통계 차트"]
    end

    subgraph Backend["백엔드 Spring Boot (포트 8080)"]
        API["REST API"]
    end

    subgraph ExternalAPI["외부 API"]
        Jira["Jira Cloud API\n(atlassian.net)"]
        Confluence["Confluence API\n(atlassian.net/wiki)"]
    end

    subgraph DB["데이터베이스"]
        H2["H2 (개발)\nin-memory"]
        PG["PostgreSQL (프로덕션)"]
    end

    User -->|"ZIP 파일 업로드\n회고 조회"| Frontend
    Frontend -->|"HTTP REST"| Backend
    Backend -->|"REST API (Basic Auth)"| Jira
    Backend -->|"REST API (Basic Auth)"| Confluence
    Backend -->|"JPA / Hibernate"| H2
    Backend -.->|"프로덕션 전환 시"| PG
```

---

## 2. 백엔드 컴포넌트 다이어그램

```mermaid
graph TB
    subgraph Controller["Controller 계층"]
        AC["AnalysisController\n/api/analyze\n/api/health"]
        JC["JiraController\n/api/jira/*\n/api/confluence/*"]
    end

    subgraph Service["Service 계층"]
        GAS["GitAnalysisService\nJGit으로 커밋 분석"]
        FPS["FileProcessingService\nZIP 압축 해제"]
        SS["StatisticsService\n통계 집계"]
        JS["JiraService\nJira/Confluence 연동"]
    end

    subgraph Repository["Repository 계층"]
        ARR["AnalysisResultRepository\n(JpaRepository)"]
    end

    subgraph Domain["Domain 모델"]
        AR["AnalysisResult\n(analysis_results 테이블)"]
        CI["CommitInfo\n(commit_infos 테이블)"]
    end

    subgraph Config["설정"]
        JConf["JiraConfig\nRestClient Bean 생성"]
        JProp["JiraProperties\n환경변수 바인딩"]
        WConf["WebConfig\nCORS 전역 설정"]
    end

    AC --> GAS
    GAS --> FPS
    GAS --> SS
    GAS --> ARR
    JC --> JS
    JS --> JConf
    JConf --> JProp
    ARR --> AR
    AR --> CI
```

---

## 3. 데이터 흐름 - Git 분석 시나리오

```mermaid
sequenceDiagram
    actor User as 개발자
    participant FE as 프론트엔드
    participant AC as AnalysisController
    participant GAS as GitAnalysisService
    participant FPS as FileProcessingService
    participant SS as StatisticsService
    participant DB as H2 DB

    User->>FE: ZIP 파일 + userName + quarter 입력
    FE->>AC: POST /api/analyze (multipart/form-data)
    AC->>GAS: analyzeRepositories(zipFiles, userName, quarter)

    loop 각 ZIP 파일
        GAS->>FPS: extractZipFile(zipFile, tempDir)
        FPS-->>GAS: 압축 해제된 디렉토리 경로
        GAS->>GAS: JGit으로 커밋 순회<br/>(author 필터링, 분기 날짜 필터)
        GAS->>SS: 통계 집계 (커밋수, 라인수, 날짜별)
    end

    GAS->>DB: AnalysisResult + CommitInfo 저장
    DB-->>GAS: 저장된 엔티티 (id 포함)
    GAS-->>AC: AnalysisResult
    AC-->>FE: AnalysisResponse (JSON)
    FE->>User: Chart.js로 통계 시각화
```

---

## 4. 데이터 흐름 - 회고 생성 시나리오 (Jira 연동)

```mermaid
sequenceDiagram
    actor User as 개발자
    participant FE as 프론트엔드
    participant JC as JiraController
    participant JS as JiraService
    participant Jira as Jira Cloud API
    participant Conf as Confluence API

    User->>FE: email + quarter + projectKey 입력
    FE->>JC: POST /api/jira/retrospective
    JC->>JS: generateRetrospectiveByEmail(request)

    JS->>Jira: GET /rest/api/3/search (완료 이슈 JQL)
    Jira-->>JS: 완료된 이슈 목록

    JS->>Jira: GET /rest/api/3/search (진행중 이슈 JQL)
    Jira-->>JS: 진행 중 이슈 목록

    opt spaceKey 있는 경우
        JS->>Conf: GET /wiki/rest/api/content
        Conf-->>JS: Confluence 페이지 목록
    end

    JS-->>JC: RetrospectiveJiraResponse
    JC-->>FE: 통합 회고 데이터 (JSON)
    FE->>User: 회고 문서 렌더링
```

---

## 5. 데이터베이스 ER 다이어그램

```mermaid
erDiagram
    ANALYSIS_RESULTS {
        bigint id PK
        varchar userName
        varchar quarter
        int totalCommits
        int totalFiles
        int linesAdded
        int linesDeleted
        text commitsByDateJson
        datetime createdAt
        datetime updatedAt
    }

    COMMIT_INFOS {
        bigint id PK
        bigint analysis_result_id FK
        varchar commitHash
        varchar authorName
        varchar authorEmail
        datetime commitDate
        text message
        int filesChanged
        int insertions
        int deletions
    }

    ANALYSIS_RESULTS ||--o{ COMMIT_INFOS : "1:N"
```

---

## 6. API 엔드포인트 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/analyze` | Git ZIP 파일 분석 |
| `GET` | `/api/health` | 헬스 체크 |
| `GET` | `/api/jira/status` | Jira 연결 상태 확인 |
| `GET` | `/api/jira/issues` | JQL 직접 검색 |
| `GET` | `/api/jira/issues/mine` | 내 이슈 (currentUser()) |
| `GET` | `/api/jira/issues/done` | 완료된 이슈 |
| `GET` | `/api/jira/issues/in-progress` | 진행 중 이슈 |
| `GET` | `/api/jira/issues/sprint` | 스프린트 이슈 |
| `GET` | `/api/jira/retrospective` | 회고 통합 데이터 (currentUser) |
| `POST` | `/api/jira/retrospective` | 이메일 기반 회고 생성 |
| `GET` | `/api/jira/projects` | 프로젝트 목록 |
| `GET` | `/api/confluence/pages` | Confluence 페이지 조회 |

---

## 7. 환경변수 설정

| 환경변수 | 설명 | 기본값 |
|----------|------|--------|
| `JIRA_BASE_URL` | Jira/Confluence 도메인 | `https://your-company.atlassian.net` |
| `JIRA_EMAIL` | Atlassian 계정 이메일 | (필수) |
| `JIRA_API_TOKEN` | Atlassian API 토큰 | (필수) |
| `JIRA_ENABLED` | Jira 연동 활성화 여부 | `true` |

---

## 8. 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | HTML, Tailwind CSS (CDN), Chart.js, Vanilla JS |
| 백엔드 | Spring Boot 3.4.1, Kotlin, JPA/Hibernate |
| Git 분석 | JGit (Eclipse JGit) |
| 데이터베이스 | H2 (개발), PostgreSQL (프로덕션) |
| 외부 연동 | Jira Cloud REST API v3, Confluence REST API |
| 인증 | Basic Auth (email + API token) |
| 빌드 | Gradle (Kotlin DSL) |
