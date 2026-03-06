# 원온원(OneOnOne) - 개발 로드맵

## 프로젝트 개요

**원온원(OneOnOne)**은 개발자의 분기별 작업 내역을 자동으로 분석하여 회고, 이력서, 피드백을 생성해주는 애플리케이션입니다.

### 핵심 기능
- Git 저장소 업로드 및 분석
- 커밋 히스토리 기반 작업 내역 추출
- 사용자 이름 기반 기여도 분석
- 분기별 회고 자동 생성
- 이력서용 프로젝트 설명 생성
- AI 기반 피드백 제공

### 기술 스택
- **Backend**: Spring Boot + Kotlin
- **Frontend**: JavaScript + Tailwind CSS
- **분석**: Git API, JGit (Java Git implementation)
- **AI**: LLM API 연동 (Claude/GPT)

---

## Phase 1: 프로젝트 설계 및 기초 구조 (1-2주)

### 1.1 요구사항 정의
- [ ] Git 저장소 업로드 방식 결정 (ZIP 업로드 vs Git Clone URL)
- [ ] 분석 대상 정보 정의 (커밋, PR, 이슈, 코드 변경량)
- [ ] 출력 형식 정의 (회고, 이력서, 피드백 템플릿)
- [ ] 사용자 식별 방식 (Git author name, email)

### 1.2 아키텍처 설계 (ADR)
- [ ] 저장소 처리 방식: 임시 저장 vs 영구 저장
- [ ] 분석 처리 방식: 동기 vs 비동기 (대용량 레포지토리 고려)
- [ ] 데이터 저장: 분석 결과 캐싱 전략
- [ ] AI 연동 방식: API 선택 및 프롬프트 설계

### 1.3 데이터베이스 설계
```sql
-- 저장소 정보
repositories (
  id, name, uploaded_at, status
)

-- 분석 결과
analysis_results (
  id, repository_id, user_name, quarter,
  commit_count, files_changed, lines_added, lines_deleted,
  created_at
)

-- 생성된 문서
generated_documents (
  id, analysis_result_id, type (회고/이력서/피드백),
  content, created_at
)
```

---

## Phase 2: MVP 개발 (2-3주)

### 2.1 Backend 핵심 기능
- [ ] **저장소 업로드 API**
  - ZIP 파일 업로드 엔드포인트
  - 임시 디렉토리 저장 및 압축 해제

- [ ] **Git 분석 엔진**
  - JGit을 사용한 커밋 히스토리 읽기
  - 사용자별 필터링 (author name/email 매칭)
  - 분기별 그룹핑 (Q1: 1-3월, Q2: 4-6월, Q3: 7-9월, Q4: 10-12월)
  - 통계 계산: 커밋 수, 변경 파일 수, 추가/삭제 라인 수

- [ ] **분석 결과 저장**
  - 분석 데이터 DB 저장
  - 조회 API 구현

### 2.2 Frontend 기본 UI
- [ ] **메인 페이지**
  - 저장소 업로드 폼 (다중 업로드 지원)
  - 분석할 사용자 이름 입력 필드
  - 분기 선택 드롭다운

- [ ] **분석 결과 페이지**
  - 커밋 통계 시각화 (차트)
  - 주요 작업 내역 타임라인
  - 생성 버튼 (회고/이력서/피드백)

- [ ] **문서 생성 페이지**
  - 생성된 문서 미리보기
  - 복사/다운로드 기능
  - 수정 기능 (선택적)

### 2.3 기본 문서 생성 로직
- [ ] **회고 템플릿**
  ```
  ## Q[n] 회고
  - 주요 성과: [커밋 기반 주요 작업]
  - 기술 스택: [변경된 파일 확장자 기반]
  - 배운 점: [패턴 분석]
  - 개선점: [제안]
  ```

- [ ] **이력서 프로젝트 설명 템플릿**
  ```
  - [프로젝트명]: [기간]
    - [주요 기여 내용]
    - 사용 기술: [...]
    - 성과: [커밋/코드량 정량화]
  ```

---

## Phase 3: AI 연동 및 고도화 (2주)

### 3.1 AI 기반 분석 강화
- [ ] LLM API 연동 (Claude API 권장)
- [ ] 커밋 메시지 의미 분석
- [ ] 코드 변경 패턴 분석 (리팩토링, 신규 개발, 버그 수정 분류)
- [ ] 개인화된 회고 생성

### 3.2 피드백 기능
- [ ] 코드 품질 분석
  - 커밋 크기 분포
  - 커밋 메시지 품질
  - 작업 패턴 (집중도, 일관성)

- [ ] 성장 제안
  - 부족한 영역 식별
  - 학습 리소스 추천

### 3.3 다중 저장소 통합 분석
- [ ] n개 저장소 동시 업로드
- [ ] 저장소별 가중치 설정
- [ ] 통합 대시보드 제공

---

## Phase 4: 사용성 개선 및 최적화 (1-2주)

### 4.1 성능 최적화
- [ ] 대용량 저장소 처리 (비동기 작업 큐)
- [ ] 분석 결과 캐싱
- [ ] 페이지네이션

### 4.2 UX 개선
- [ ] 로딩 상태 표시
- [ ] 에러 핸들링 강화
- [ ] 반응형 디자인 (모바일 대응)

### 4.3 추가 기능
- [ ] 분석 결과 비교 (분기별, 연도별)
- [ ] PDF/Markdown 내보내기
- [ ] 저장소 즐겨찾기

---

## Phase 5: 배포 및 운영 (1주)

### 5.1 배포 준비
- [ ] Docker 컨테이너화
- [ ] 환경 변수 설정 (API 키 등)
- [ ] CI/CD 파이프라인 구축

### 5.2 보안
- [ ] 업로드 파일 검증 (악성 코드 방지)
- [ ] 저장소 자동 삭제 (개인정보 보호)
- [ ] API Rate Limiting

### 5.3 모니터링
- [ ] 에러 로깅
- [ ] 사용량 추적

---

## 기술 상세 설계

### Backend 구조 (Spring Boot + Kotlin)
```
src/main/kotlin/
├── controller/
│   ├── RepositoryController.kt      # 저장소 업로드 API
│   ├── AnalysisController.kt        # 분석 실행 API
│   └── DocumentController.kt        # 문서 생성 API
├── service/
│   ├── GitAnalysisService.kt        # JGit 분석 로직
│   ├── StatisticsService.kt         # 통계 계산
│   ├── AIService.kt                 # LLM 연동
│   └── DocumentGenerationService.kt # 문서 생성
├── domain/
│   ├── Repository.kt
│   ├── AnalysisResult.kt
│   └── GeneratedDocument.kt
└── repository/
    └── (JPA Repositories)
```

### Frontend 구조 (JavaScript + Tailwind CSS)
```
public/
├── index.html
├── css/
│   └── styles.css              # Tailwind 커스텀
├── js/
│   ├── upload.js               # 파일 업로드 로직
│   ├── analysis.js             # 분석 결과 표시
│   ├── chart.js                # Chart.js 통계 시각화
│   └── document.js             # 문서 생성 UI
└── components/
    ├── header.html
    └── footer.html
```

### 핵심 라이브러리
- **JGit**: Git 저장소 분석
- **Spring WebFlux**: 비동기 처리 (선택적)
- **Chart.js**: 데이터 시각화
- **Marked.js**: Markdown 렌더링

---

## 우선순위

### 🔴 High Priority (MVP 필수)
1. Git 저장소 업로드 및 분석
2. 사용자별 커밋 필터링
3. 기본 회고 문서 생성

### 🟡 Medium Priority (Phase 3)
1. AI 기반 고급 분석
2. 피드백 생성
3. 다중 저장소 통합

### 🟢 Low Priority (추후 개선)
1. PDF 내보내기
2. 저장소 비교 기능
3. 팀 단위 분석

---

## 예상 일정

| Phase | 기간 | 주요 산출물 |
|-------|------|------------|
| Phase 1 | 1-2주 | 설계 문서, DB 스키마 |
| Phase 2 | 2-3주 | MVP (기본 분석 + UI) |
| Phase 3 | 2주 | AI 연동, 고급 분석 |
| Phase 4 | 1-2주 | 성능/UX 개선 |
| Phase 5 | 1주 | 배포, 운영 준비 |

**총 예상 기간**: 7-10주

---

## 다음 단계

1. **요구사항 명확화**: 사용자 시나리오 구체화
2. **기술 검증**: JGit 프로토타입 개발
3. **UI 목업**: Figma 디자인 (선택적)
4. **Phase 1 시작**: ADR 작성 및 DB 설계

---

## 참고사항

- 이 로드맵은 Cursor Rules 14-step 프레임워크를 따라 단계별로 진행할 수 있습니다.
- 각 Phase별로 설계 검토(doc07)와 품질 보증(doc12)을 수행하는 것을 권장합니다.
- MVP 완성 후 실제 사용자 피드백을 받아 우선순위를 조정하세요.
