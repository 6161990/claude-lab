# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 참고하는 가이드를 제공합니다.

## 저장소 개요

이 저장소는 Cursor와 Claude Code를 사용한 AI 기반 개발 워크플로우를 학습하기 위한 워크샵 저장소입니다. 다음 내용을 포함합니다:

- **Cursor Rules 14단계 프레임워크**: 풀스택 개발을 위한 구조화된 프롬프트 엔지니어링 방법론
- **실습 예제**: 프롬프트 엔지니어링 기법을 위한 실습 튜토리얼

## 언어 및 커뮤니케이션 규칙

- **기본 응답 언어**: 한국어
- **코드 주석**: 한국어로 작성
- **커밋 메시지**: 한국어로 작성
- **문서화**: 한국어로 작성
- **변수명/함수명**: 영어 camelCase 사용 (코드 표준 준수)

## Git 커밋 규칙

Git 커밋과 관련된 상세 규칙은 [references/git-commit-rules.md](references/git-commit-rules.md)를 참고하세요.

**핵심 요약:**
- 작업 컨텍스트가 1개: 단순 명시
- 작업 컨텍스트가 2개: '및' 키워드로 연결
- 작업 컨텍스트가 3개 이상: 커밋을 분리하여 각각 커밋

## 저장소 구조

```
claude-lab/
├── references/                  # 참고 문서 및 가이드
│   ├── git-commit-rules.md     # Git 커밋 규칙
│   ├── Cursor_Rules_14steps/   # 14단계 개발 프로세스 프롬프트 (.mdc 파일)
│   │   ├── doc01-requirements.mdc              # 요구사항 정의
│   │   ├── doc02-adr.mdc                       # 아키텍처 의사결정 기록
│   │   ├── doc03-database.mdc                  # 데이터베이스 설계
│   │   ├── doc04-api-spec.mdc                  # API 명세
│   │   ├── doc05-ui-concept-prototype.mdc      # UI 컨셉 및 프로토타이핑
│   │   ├── doc06-detailed-design.mdc           # 상세 설계 (4+1 뷰)
│   │   ├── doc07-design-review-procedure.mdc   # 설계 검토 절차
│   │   ├── doc08-prototype-analysis.mdc        # 프로토타입 분석
│   │   ├── doc09-implementation-plan.mdc       # 구현 계획
│   │   ├── doc10-implementation-generation.mdc # 코드 생성
│   │   ├── doc11-test-generation.mdc           # 테스트 생성
│   │   ├── doc12-quality-assurance-validation.mdc # 품질 보증
│   │   ├── doc13-debug.mdc                     # 디버깅 지원
│   │   └── doc14-ai-task-failure-analysis.mdc  # AI 작업 실패 분석
│   └── practice/               # 실습 예제 (한국어)
│       ├── 실습1-*.md          # 프롬프트 엔지니어링 기초
│       └── 실습3-*.md          # 고급 실습
```

## 14단계 개발 프레임워크

Cursor Rules 프레임워크는 개발의 각 단계별로 구조화된 프롬프트를 제공합니다:

### 설계 단계 (5단계)
1. **요구사항 정의** - 사용자 요청을 실행 가능한 요구사항으로 변환
2. **아키텍처 의사결정** - 기술적 선택과 근거 문서화 (ADR)
3. **데이터베이스 설계** - ER 다이어그램, 정규화, 스키마 정의
4. **API 명세** - OpenAPI 형식의 RESTful API 설계
5. **UI 프로토타이핑** - 디자인 시스템 및 컴포넌트 프로토타이핑

### 상세 설계 및 검토 (2단계)
6. **상세 설계** - 4+1 뷰 모델을 사용한 시스템 명세
7. **설계 검토** - 이해도 검증 및 품질 개선

### 분석 및 계획 (2단계)
8. **프로토타입 분석** - 5가지 품질 축(보안, 성능, 가용성, 유지보수성, 운영성)을 사용한 프로덕션 준비도 평가
9. **구현 계획** - 단계별 프로덕션 마이그레이션 전략

### 구현 및 테스팅 (2단계)
10. **코드 생성** - 명세로부터 프로덕션 코드 생성
11. **테스트 생성** - 계층별 테스트 생성 (단위, 통합, E2E)

### 품질 보증 및 개선 (3단계)
12. **품질 검증** - 설계-구현 일관성 자동 검증
13. **디버깅** - 근본 원인 분석 및 체계적 오류 해결
14. **실패 분석** - AI 작업 실패로부터 학습하여 지속적 개선

## 기술 스택 (프레임워크 문서 기준)

이 프레임워크는 다음 기술을 위해 설계되었지만, 다른 기술로도 적용 가능합니다:

**프론트엔드:**
- Next.js 14+ (App Router), React, TypeScript
- shadcn/ui + Radix UI, Tailwind CSS
- Jest, React Testing Library, Cypress/Playwright

**백엔드:**
- Python 3.8+, FastAPI, Pydantic, SQLAlchemy
- PostgreSQL (프로덕션), SQLite (개발)
- pytest, pytest-mock, TestContainers

**데브옵스:**
- Docker, Docker Compose
- Git, GitHub, CI/CD 파이프라인

**설계:**
- Mermaid 다이어그램, Figma API 통합
- 4+1 뷰 모델, ADR 문서화

## .mdc 파일 사용법

`.mdc` 파일은 Cursor 전용 프롬프트 템플릿입니다. Cursor에서 다음과 같이 참조합니다:

```
@doc01-requirements.mdc를 사용하여 다음 요구 사항을 분석하십시오.
[여기에 요구사항 입력]
```

Claude Code 사용자를 위한 참고사항: 이 파일들은 각 개발 단계별로 역할, 작업, 단계별 지침을 정의하는 구조화된 프롬프트를 포함합니다. 방법론을 적용하기 전에 관련 .mdc 파일을 읽어 이해하세요.

## 실습 예제

`references/practice/` 디렉토리에는 한국어 실습 자료가 포함되어 있습니다:
- **실습1 시리즈**: 기본 프롬프트 엔지니어링 패턴 (Role-Task-Instructions 형식, few-shot 예제, Chain-of-Thought)
- **실습3 시리즈**: 구조화된 출력, Python 코드 예제를 포함한 고급 실습

## 개발 워크플로우 철학

이 프레임워크는 다음을 강조합니다:
- **중요한 의사결정 시점에서의 사람 개입 검증**
- **점진적 품질 게이트** - 다음 단계로 진행하기 전 검증
- **문서 주도 개발** - 구현 전 포괄적인 설계
- **리스크 기반 우선순위화** - 영향도, 발생 가능성, 노력 평가
- **프로토타입-프로덕션 갭 분석** - 체계적인 프로덕션 준비도 평가

## 핵심 원칙

1. **구조화된 프롬프팅**: 예제와 함께 Role-Task-Instructions 형식 사용
2. **단계별 게이트**: 구현 전 설계 검증 완료
3. **품질 메트릭**: >90% 커버리지, >95% 구조적 일관성 유지
4. **반복적 개선**: 각 단계에서 질문 및 명확화 과정 포함
5. **실패로부터의 학습**: AI 작업 실패 문서화 및 분석 (doc14)
