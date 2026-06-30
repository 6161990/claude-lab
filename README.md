# claude-lab: AI 기반 개발 워크숍 & 실험실

> Cursor Rules 14단계 프레임워크를 학습하고, Claude Code로 AI 자동화 워크플로우를 구축하는 저장소

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Framework](https://img.shields.io/badge/framework-14%20Steps-blue.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

## 📋 저장소 개요

이 저장소는 두 가지 목표를 갖고 있습니다:

1. **학습**: Cursor Rules 14단계 개발 프레임워크를 이해하고 실습
2. **실험**: Claude Code + MCP를 활용한 AI 자동화 도구 개발

### 주요 프로젝트

#### 1️⃣ OneOnOne - 개발자 회고 보고서 생성기
Git 저장소를 업로드하면 AI가 커밋 이력과 소스코드를 분석하여 개발자 회고 보고서를 자동으로 작성합니다.

- **Stack**: Spring Boot 3.4.1 + Kotlin + Next.js 14 + TypeScript
- **AI**: Claude API (claude-sonnet-4-6)
- **기능**: 다중 저장소 분석, Jira/Confluence 연동, 커스텀 프롬프트

#### 2️⃣ AI 자동화 스킬 (MCP 기반)
Claude Code에서 사용 가능한 자동화 도구들:

| 스킬 | 설명 |
|------|------|
| **trading-volume** | 네이버 프리미엄콘텐츠 매매일지 분석 → 거래대금 리포트 자동 생성 |
| **blog-post** | 사진 + 소재 → 네이버 블로그 포스팅 자동 발행 |
| **ai-video** | 참고 영상/주제 → 완성된 AI 쇼츠 제작 (기획~편집) |
| **feature-develop** | OneOnOne 기능 개발 오케스트레이터 (백엔드+프론트엔드+QA) |

#### 3️⃣ 개발 학습 자료
Cursor Rules 프레임워크의 각 단계별 가이드:

```
references/developWorkflow/
├── doc01-requirements.mdc          # 요구사항 정의
├── doc02-adr.mdc                   # 아키텍처 의사결정
├── doc03-database.mdc              # 데이터베이스 설계
├── doc04-api-spec.mdc              # API 명세
├── doc05-ui-concept-prototype.mdc  # UI 프로토타이핑
├── doc06-detailed-design.mdc       # 상세 설계 (4+1 뷰)
├── doc07-design-review.mdc         # 설계 검토
├── doc08-prototype-analysis.mdc    # 프로토타입 분석
├── doc09-implementation-plan.mdc   # 구현 계획
├── doc10-implementation-generation.mdc # 코드 생성
├── doc11-test-generation.mdc       # 테스트 생성
├── doc12-quality-assurance.mdc     # 품질 보증
├── doc13-debug.mdc                 # 디버깅
└── doc14-ai-task-failure-analysis.mdc # 실패 분석
```

참고: Cursor 사용자는 `@doc01-requirements.mdc` 형식으로 프롬프트에 참조 가능

## 🗂️ 프로젝트 구조

```
claude-lab/
├── OneOnOne/                        # 풀스택 웹 애플리케이션
│   ├── backend/                     # Spring Boot + Kotlin
│   └── frontend/                    # Next.js + React + TypeScript
├── blog/                            # 블로그 자동화 (MCP 서버)
│   ├── nepcon-mcp/                  # 네이버 프리미엄콘텐츠 MCP
│   ├── mcp-server/                  # 커스텀 MCP 서버
│   ├── prompts/                     # AI 프롬프트 모음
│   └── photo/                       # 블로그 사진 자료
├── references/                      # 14단계 개발 프레임워크
│   ├── developWorkflow/             # .mdc 가이드 문서
│   ├── practice/                    # 실습 예제
│   └── git/                         # Git 커밋 규칙
├── .claude/                         # Claude Code 설정
│   ├── agents/                      # 커스텀 에이전트
│   ├── skills/                      # MCP 기반 스킬
│   ├── commands/                    # 슬래시 명령어
│   └── plans/                       # 작업 계획
└── docs/                            # 추가 문서
```

## 🚀 빠른 시작

### OneOnOne 실행

#### 사전 준비
- JDK 21+
- Node.js 18+
- Anthropic API 키

#### 백엔드 (포트 8080)

```bash
cd OneOnOne/backend
export ANTHROPIC_API_KEY=sk-ant-...
./gradlew bootRun
```

#### 프론트엔드 (포트 3000)

```bash
cd OneOnOne/frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
npm run dev
```

### OneOnOne 사용 방법

1. **저장소 준비**: Git 저장소를 ZIP으로 압축
   ```bash
   cd /path/to/your/project
   zip -r repo.zip . --exclude "*/node_modules/*" "*/build/*" "*/.next/*"
   ```

2. **정보 입력**: 웹 폼에 다음을 입력
   - ZIP 파일 (최대 3개, 각 500MB)
   - Git author 이름/이메일
   - 분석 기간 (시작일~종료일)
   - (선택) Jira 이메일, 커스텀 프롬프트

3. **분석 시작**: "분석 시작" 버튼 클릭 후 결과 확인

### MCP 스킬 활용

Claude Code에서 다음 스킬을 바로 사용할 수 있습니다:

```bash
# 네프콘 매매일지 분석
/trading-volume <네프콘_URL>

# 블로그 포스팅 자동 발행
/blog-post <소재> <사진_파일명>

# AI 영상 제작
/ai-video <참고_영상_또는_주제>

# OneOnOne 기능 개발
/feature-develop <기능_설명>
```

## 📚 개발 프레임워크

### 14단계 워크플로우
이 저장소의 핵심은 Cursor Rules **14단계 개발 프레임워크**입니다. 각 단계는 구조화된 가이드를 제공합니다:

```
설계 (1-5)          상세설계 (6-7)      분석 (8-9)      구현 (10-11)     품질보증 (12-14)
요구사항 ─→ ADR ─→ DB설계 ─→ API설계 ─→ UI설계 ──→ 상세설계 ──→ 설계검토 ──→ 프로토 분석
                                                                        ↓
                                                                    구현계획 ──→ 코드생성
                                                                               ↓
                                                                           테스트생성
                                                                               ↓
                                                                           품질검증
                                                                               ↓
                                                                              디버깅
```

### 참고 자료

- **프레임워크 문서**: `references/developWorkflow/doc*.mdc`
- **실습 예제**: `references/practice/`
- **커밋 규칙**: `references/git/git-commit-rules.md`

Cursor 사용자는 프롬프트에서 다음과 같이 참조:
```
@doc01-requirements.mdc를 사용하여 다음 요구사항을 분석하세요:
[요구사항 내용]
```

## 🔧 주요 기술 스택

| 계층 | 기술 |
|------|------|
| **Frontend** | Next.js 14, React, TypeScript, shadcn/ui |
| **Backend** | Spring Boot 3.4.1, Kotlin 2.1.0, JGit |
| **AI** | Claude API (claude-sonnet-4-6) |
| **DevOps** | Docker, GitHub Actions |
| **MCP** | Claude MCP for custom tools |

## 🎯 핵심 원칙

1. **단계별 게이트**: 구현 전 설계 완료
2. **품질 메트릭**: 테스트 커버리지 >90%
3. **문서 주도 개발**: 구현보다 설계 문서 우선
4. **AI 자동화**: 반복 작업은 MCP 스킬화
5. **실패로부터 학습**: 문제 분석 및 개선 (doc14)

## 💬 언어 규칙

- **응답 언어**: 한국어
- **코드 주석**: 한국어
- **커밋 메시지**: 한국어 (규칙: `references/git/git-commit-rules.md`)
- **변수/함수명**: 영어 camelCase

## 📖 API

### POST /api/analyze

```
Content-Type: multipart/form-data

Parameters:
  repositories: File[]       # ZIP 파일 (1~3개)
  userName:     string       # Git author 이름 또는 이메일
  startDate:    string       # YYYY-MM-DD
  endDate:      string       # YYYY-MM-DD
  jiraEmail:    string?      # (선택)
  customPrompt: string?      # (선택)
```

Response:
```json
{
  "userName": "개발자명",
  "startDate": "2025-01-01",
  "endDate": "2025-03-31",
  "analysis": "## 1. 이번 분기 핵심 기여\n..."
}
```

### GET /api/health

서버 헬스 체크

## 🌍 환경변수

```bash
# 필수
ANTHROPIC_API_KEY=sk-ant-...

# 선택
ANTHROPIC_MODEL=claude-sonnet-4-6
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=service-account@company.com
JIRA_API_TOKEN=your-token
JIRA_ENABLED=false
```

## 📜 라이선스

MIT License

---

**Made with Claude Code** | 최종 업데이트: 2026-06-27
