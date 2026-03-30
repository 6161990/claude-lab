---
name: feature-develop
description: "OneOnOne 프로젝트의 기능 개발 오케스트레이터. 백엔드(Spring Boot/Kotlin)와 프론트엔드(Next.js/React)를 병렬로 구현하고, QA로 통합 정합성을 검증하는 전체 워크플로우를 조율한다. '기능 개발', '기능 구현', '새 기능 추가', 'feature 개발', '풀스택 구현', '백엔드+프론트엔드 구현' 요청 시 반드시 이 스킬을 사용할 것. 단순 버그 수정이나 단일 파일 수정에는 사용하지 않는다."
---

# Feature Develop Orchestrator

OneOnOne 프로젝트의 기능 개발을 조율하는 오케스트레이터. 백엔드와 프론트엔드를 병렬로 구현하고, QA로 통합 정합성을 검증한다.

## 실행 모드: 서브 에이전트

백엔드/프론트엔드가 독립적으로 작업하고 결과를 전달하는 구조이므로, 서브 에이전트 모드가 적합하다.

## 에이전트 구성

| 에이전트 | subagent_type | 역할 | 출력 |
|---------|--------------|------|------|
| backend-developer | backend-developer | Spring Boot API + 서비스 구현 | `_workspace/02_backend_{feature}.md` |
| frontend-developer | frontend-developer | Next.js 페이지 + 컴포넌트 구현 | `_workspace/02_frontend_{feature}.md` |
| qa-reviewer | qa-reviewer | 통합 정합성 검증 | `_workspace/03_qa_{feature}_report.md` |

## 워크플로우

### Phase 1: 요구사항 분석 및 설계

사용자의 기능 요청을 분석하여 구현 계획을 수립한다.

1. 사용자 요청에서 기능 범위를 파악한다
2. `_workspace/` 디렉토리를 생성한다
3. 기존 코드를 탐색하여 영향 범위를 파악한다
4. 구현 계획을 수립한다:
   - 백엔드: 필요한 API 엔드포인트, DTO, 서비스 로직
   - 프론트엔드: 필요한 페이지, 컴포넌트, 훅
   - 공유 인터페이스: API 요청/응답 형식 (양쪽이 합의할 계약)
5. 공유 인터페이스를 `_workspace/01_api_contract.md`에 기록한다

**공유 인터페이스 형식:**
```markdown
## API 계약: {기능명}

### 엔드포인트
- Method: {GET/POST/PUT/DELETE}
- Path: /api/{path}
- Request: {요청 형식}
- Response: {응답 DTO 구조 - 필드명은 camelCase}

### 데이터 모델
- {DTO 이름}: {필드 목록}
```

### Phase 2: 병렬 구현 (팬아웃)

백엔드와 프론트엔드를 병렬로 구현한다. 단일 메시지에서 2개 Agent 도구를 동시 호출한다.

| 에이전트 | 입력 | 출력 | model | run_in_background |
|---------|------|------|-------|-------------------|
| backend-developer | API 계약 + 기능 요구사항 | 구현된 Kotlin 소스 파일 | opus | true |
| frontend-developer | API 계약 + 기능 요구사항 | 구현된 TSX/TS 소스 파일 | opus | true |

**에이전트 프롬프트에 반드시 포함할 내용:**
- `_workspace/01_api_contract.md`를 Read로 읽어 API 계약을 확인하라
- 구현 완료 후 변경한 파일 목록을 `_workspace/02_{role}_{feature}.md`에 기록하라
- 기존 코드 패턴을 따르라 (새 패턴 도입 금지)

### Phase 3: QA 검증 (검증)

양쪽 구현이 완료되면 QA 에이전트로 통합 정합성을 검증한다.

| 에이전트 | 입력 | 출력 | model |
|---------|------|------|-------|
| qa-reviewer | Phase 2 산출물 + API 계약 | 검증 리포트 | opus |

**QA 프롬프트에 반드시 포함할 내용:**
- `_workspace/01_api_contract.md`와 실제 구현을 대조하라
- 백엔드 DTO 필드명과 프론트엔드 타입 필드명을 교차 비교하라
- 빌드 성공 여부를 확인하라 (`./gradlew build`, `npm run build`)
- 리포트를 `_workspace/03_qa_{feature}_report.md`에 저장하라

### Phase 4: 수정 및 완료

QA 리포트에서 실패 항목이 있으면 수정한다.

1. QA 리포트를 Read로 확인한다
2. 실패 항목이 있으면:
   - 백엔드 이슈: backend-developer 에이전트를 재호출하여 수정
   - 프론트엔드 이슈: frontend-developer 에이전트를 재호출하여 수정
   - 최대 2회 재시도 후에도 실패하면 사용자에게 알린다
3. `_workspace/` 디렉토리를 보존한다 (사후 검증용)
4. 사용자에게 결과를 요약 보고한다

## 데이터 흐름

```
사용자 요청
    ↓
[Phase 1: 설계] → _workspace/01_api_contract.md
    ↓
[Phase 2: 팬아웃]
    ├→ [backend-developer]  → Kotlin 소스 + _workspace/02_backend_{feature}.md
    └→ [frontend-developer] → TSX/TS 소스 + _workspace/02_frontend_{feature}.md
    ↓
[Phase 3: QA] → [qa-reviewer] → _workspace/03_qa_{feature}_report.md
    ↓
[Phase 4: 수정/완료] → 사용자에게 결과 보고
```

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| 에이전트 1개 실패 | 1회 재시도. 재실패 시 해당 결과 없이 QA 진행, 리포트에 누락 명시 |
| 에이전트 과반 실패 | 사용자에게 알리고 진행 여부 확인 |
| QA 실패 항목 존재 | 해당 에이전트 재호출로 수정 (최대 2회) |
| 빌드 실패 | 에러 로그 분석 후 수정 에이전트 재호출 |
| API 계약 불명확 | Phase 1에서 사용자에게 확인 요청 |

## 스킵 가능한 Phase

모든 기능이 풀스택은 아니다. 상황에 따라 Phase를 스킵한다:

| 상황 | 스킵 |
|------|------|
| 백엔드만 변경 | frontend-developer 스킵, QA는 백엔드 빌드만 검증 |
| 프론트엔드만 변경 | backend-developer 스킵, QA는 프론트 빌드만 검증 |
| 단순 수정 (파일 1-2개) | 이 오케스트레이터를 사용하지 않고 직접 수정 |

## 테스트 시나리오

### 정상 흐름
1. 사용자가 "분석 결과에 PDF 내보내기 기능 추가해줘" 요청
2. Phase 1에서 API 계약 수립 (POST /api/export/pdf, 응답 DTO 정의)
3. Phase 2에서 backend-developer와 frontend-developer 병렬 실행
4. Phase 3에서 qa-reviewer가 DTO ↔ 타입 교차 검증, 빌드 검증
5. QA PASS → 사용자에게 완료 보고

### 에러 흐름
1. Phase 2에서 frontend-developer가 에러로 실패
2. 1회 재시도 후에도 실패
3. backend-developer 결과만으로 Phase 3 QA 진행
4. QA 리포트에 "프론트엔드 미구현" 명시
5. 사용자에게 부분 완료 알림 + 프론트엔드 이슈 설명