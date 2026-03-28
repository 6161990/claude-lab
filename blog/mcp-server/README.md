# 네이버 블로그 MCP 서버

Claude Code에서 네이버 블로그(콩콩이대작전)를 직접 운영할 수 있는 MCP 서버입니다.
Playwright 브라우저 자동화로 스마트에디터 ONE에 글을 작성하고 발행합니다.

## 설치

```bash
cd blog/mcp-server
pip install -r requirements.txt
playwright install chromium
```

## 환경 변수 설정

프로젝트 루트의 `.env` 파일에 네이버 계정 정보를 입력하세요:

```bash
cp .env.example .env
# .env 파일을 열어 NAVER_ID, NAVER_PASSWORD, NAVER_BLOG_ID 입력
```

> **보안 주의**: `.env` 파일은 절대 git에 커밋하지 마세요. `.gitignore`에 이미 포함되어 있습니다.

## 첫 실행 (세션 초기화)

최초 실행 시 브라우저 창이 열리며 로그인을 진행합니다.

```bash
python server.py
```

- **2단계 인증**: SMS 인증 등이 발생하면 브라우저에서 직접 처리하세요.
- 로그인 성공 후 `.naver_session.json` 파일이 생성됩니다.
- 이후부터는 저장된 세션을 재사용하여 자동 로그인됩니다.

## 사용 가능한 도구

| 도구 | 설명 |
|------|------|
| `post_blog` | 새 포스팅 발행 (제목, 본문, 카테고리, 태그) |
| `save_draft` | 임시저장 |
| `list_drafts` | 임시저장 목록 조회 |
| `get_categories` | 카테고리 목록 조회 |

## 스킬 사용법 (Claude Code)

```
/blog-post 오늘 연남동 카페 다녀온 이야기
/blog-plan 2026-04
```

---

## 선택자 업데이트 가이드

네이버가 스마트에디터 ONE의 DOM 구조를 업데이트하면 자동화가 동작하지 않을 수 있습니다.
이 경우 `smart_editor.py` 상단의 `SELECTORS` 딕셔너리를 아래 방법으로 업데이트하세요.

### 선택자 확인 방법

1. Claude Code에서 Playwright MCP의 `browser_navigate`로 글쓰기 페이지 접속
2. `browser_snapshot`으로 현재 DOM 구조 확인
3. 변경된 선택자를 `SELECTORS` 딕셔너리에 업데이트

```python
# smart_editor.py
SELECTORS = {
    "title": ".se-title-input",        # ← 제목 입력 선택자
    "editor_frame": "iframe.se-main-iframe",  # ← 에디터 iframe 선택자
    "editor_body": ".se-component-content",   # ← 에디터 본문 선택자
    "publish_btn": ".publish_btn, button:has-text('발행')",
    "publish_confirm": ".confirm_btn, button:has-text('확인')",
    "draft_btn": ".save_draft_btn, button:has-text('임시저장')",
    "category_dropdown": ".category_wrap, .se-category-select",
    "tag_input": ".tag_editor input, input[placeholder*='태그']",
}
```

### 세션 초기화

세션이 만료된 경우 `.naver_session.json`을 삭제하고 재실행하면 됩니다:

```bash
rm .naver_session.json
python server.py
```
