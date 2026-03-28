---
description: "소재와 사진 파일명을 주면 콩콩 스타일로 글 작성 → 사진 삽입 → 네이버 블로그 발행까지 전부 자동으로 처리합니다."
argument-hints: "포스팅 주제/경험 설명. 사진이 있으면 '사진: 파일명1.jpg, 파일명2.jpg' 형식으로 추가"
allowed-tools:
  - Task
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_evaluate
  - mcp__playwright__browser_file_upload
  - mcp__playwright__browser_press_key
  - mcp__playwright__browser_type
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_wait_for
---

# /blog-post 워크플로우

콩콩이대작전 블로그에 소재와 사진만 주면 알아서 포스팅합니다.

## 사진 디렉토리
사진 파일은 `/Users/j6161990/Documents/GitHub/claude-lab/blog/photo/` 에 두세요.
파일명만 알려주시면 절대경로로 자동 변환합니다.

## 카테고리
소재를 보고 아래 4개 중 자동 선택:
- **일상**: 일상, 산책, 피크닉, 소소한 이야기
- **카페**: 카페 방문, 음료, 베이커리
- **맛집**: 음식점, 식당, 맛집 리뷰
- **여행**: 국내외 여행, 나들이

## 실행 단계

### 1단계: 입력 파싱
`$ARGUMENTS`에서 아래 두 가지를 분리합니다:
- **소재**: 포스팅 주제, 경험, 메모
- **사진**: `사진:` 키워드 뒤에 오는 파일명 목록 (없으면 텍스트만 발행)

```
예시 입력:
"오늘 연남동 카페 다녀왔어, 라떼 맛있었고 인테리어 너무 예뻤음. 사진: cafe1.jpg, cafe2.jpg, cafe3.jpg"
```

### 2단계: 글 작성
`blog-writer` 에이전트를 호출하여 콩콩 스타일 초안 생성.

사진이 있는 경우 본문에 `[사진1]`, `[사진2]` 등 **사진 삽입 위치 마커**를 포함하도록 지시.
`blog/prompts/meta-prompt.md` 문체 규칙 적용.

### 3단계: 글쓰기 페이지 이동
```
https://blog.naver.com/PostWriteForm.naver?blogId=kong__home
```
로그인이 필요하면 `https://nid.naver.com/nidlogin.login?mode=form` 으로 이동 후:
- JS evaluate로 ID/PW 입력 후 로그인 버튼 클릭
- `.env` 파일의 `NAVER_ID`, `NAVER_PASSWORD` 사용

### 4단계: 제목 입력
1. `.se-title-text` 요소 포커스
2. 클립보드(navigator.clipboard.writeText)로 제목 복사 후 Meta+v 붙여넣기

### 5단계: 본문 및 사진 삽입
사진 없는 경우:
- 본문 영역 클릭 후 클립보드 붙여넣기

사진 있는 경우 (마커 위치에 사진 삽입):
1. 본문을 `[사진N]` 마커 기준으로 분할
2. 각 텍스트 블록 입력 후 사진 삽입 반복:
   ```
   텍스트 블록 입력
   → "사진 추가" 버튼 클릭 (툴바의 사진 아이콘)
   → file chooser 트리거 대기
   → mcp__playwright__browser_file_upload로 /Users/j6161990/blog/photo/파일명 전달
   → 업로드 완료 대기
   → 다음 텍스트 블록 입력
   ```

### 6단계: 카테고리 · 태그 · 발행
1. "발행" 버튼 클릭 → 발행 설정 패널 오픈
2. 카테고리 드롭다운에서 소재에 맞는 카테고리 선택 (일상 / 카페 / 맛집 / 여행)
3. 태그 입력창에 추천 태그 순서대로 입력 (Enter로 구분)
4. 최종 "발행" 버튼 클릭
5. 발행 완료 후 포스팅 URL 안내

---

## 사용 예시

```
# 텍스트만
/blog-post 오늘 한강 피크닉 다녀온 이야기

# 사진 포함
/blog-post 연남동 감성 카페 발견했어! 라떼 비주얼 미쳤음. 사진: cafe1.jpg, cafe2.jpg

# 여행기 + 사진 여러 장
/blog-post 제주도 2박3일. 성산일출봉, 우도, 흑돼지 먹음. 사진: jeju1.jpg, jeju2.jpg, jeju3.jpg, jeju4.jpg

# 맛집 리뷰
/blog-post 홍대 파스타 맛집. 까르보나라 진짜 맛있었고 분위기도 좋음. 사진: pasta1.jpg, pasta2.jpg
```

## 에러 처리
- 로그인 세션 만료 → 자동 재로그인
- 사진 파일 없음 → 해당 파일 건너뛰고 계속 진행 후 사용자에게 알림
- 업로드 실패 → 재시도 1회 후 텍스트만 발행