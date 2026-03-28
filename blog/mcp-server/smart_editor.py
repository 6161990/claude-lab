"""
네이버 스마트에디터 ONE 자동화 모듈

네이버 블로그 글쓰기 페이지(스마트에디터 ONE)에 대한 Playwright 자동화를 담당합니다.

주의: 스마트에디터 ONE은 iframe 기반의 heavy JS 에디터입니다.
      네이버 업데이트 시 선택자가 변경될 수 있으므로 README.md의 '선택자 업데이트 가이드'를 참고하세요.
"""

import asyncio
import random

from playwright.async_api import Page

BLOG_WRITE_URL_TEMPLATE = (
    "https://blog.naver.com/PostWriteForm.naver?blogId={blog_id}"
)


async def random_delay(min_sec: float = 0.5, max_sec: float = 1.5):
    await asyncio.sleep(random.uniform(min_sec, max_sec))


# 스마트에디터 ONE 선택자 상수
# 네이버 업데이트 시 이 값들을 수정하세요. (README.md 참고)
SELECTORS = {
    # 제목 입력 영역
    "title": ".se-title-input",
    # 에디터 본문 iframe (frame name 또는 locator)
    "editor_frame": "iframe.se-main-iframe",
    # 에디터 본문 내 편집 가능 영역
    "editor_body": ".se-component-content",
    # 발행 버튼
    "publish_btn": ".publish_btn, button:has-text('발행')",
    # 발행 확인 팝업의 확인 버튼
    "publish_confirm": ".confirm_btn, button:has-text('확인')",
    # 임시저장 버튼
    "draft_btn": ".save_draft_btn, button:has-text('임시저장')",
    # 카테고리 선택 드롭다운
    "category_dropdown": ".category_wrap, .se-category-select",
    # 태그 입력 필드
    "tag_input": ".tag_editor input, input[placeholder*='태그']",
}


class SmartEditorAutomation:
    """네이버 스마트에디터 ONE Playwright 자동화"""

    def __init__(self, page: Page, blog_id: str):
        self.page = page
        self.blog_id = blog_id
        self.write_url = BLOG_WRITE_URL_TEMPLATE.format(blog_id=blog_id)

    async def write_post(
        self,
        title: str,
        content: str,
        category: str | None = None,
        tags: list[str] | None = None,
        publish_now: bool = True,
    ) -> dict:
        """스마트에디터를 통해 포스팅을 작성하고 발행 또는 임시저장합니다.

        Args:
            title: 포스팅 제목
            content: 포스팅 본문 (일반 텍스트 또는 HTML)
            category: 카테고리 이름 (None이면 기본 카테고리)
            tags: 태그 목록
            publish_now: True면 즉시 발행, False면 임시저장

        Returns:
            {"status": "success", "action": "published" | "draft", "url": str | None}
        """
        # 1. 글쓰기 페이지로 이동
        await self.page.goto(self.write_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay(1.0, 2.0)

        # 2. 제목 입력
        await self._input_title(title)

        # 3. 본문 입력
        await self._input_content(content)

        # 4. 카테고리 설정 (선택사항)
        if category:
            await self._set_category(category)

        # 5. 태그 입력 (선택사항)
        if tags:
            await self._input_tags(tags)

        # 6. 발행 또는 임시저장
        if publish_now:
            result_url = await self._publish()
            return {"status": "success", "action": "published", "url": result_url}
        else:
            await self._save_draft()
            return {"status": "success", "action": "draft", "url": None}

    async def _input_title(self, title: str):
        """제목 입력"""
        try:
            title_el = self.page.locator(SELECTORS["title"])
            await title_el.wait_for(timeout=10000)
            await title_el.click()
            await random_delay(0.3, 0.5)
            await title_el.fill(title)
            await random_delay(0.3, 0.7)
        except Exception as e:
            raise RuntimeError(f"제목 입력 실패: {e}\n선택자를 확인하세요: {SELECTORS['title']}")

    async def _input_content(self, content: str):
        """본문 입력 (클립보드 붙여넣기 방식)"""
        try:
            # iframe 내부 에디터 본문 영역 클릭
            frame_locator = self.page.frame_locator(SELECTORS["editor_frame"])
            body = frame_locator.locator(SELECTORS["editor_body"]).first
            await body.wait_for(timeout=10000)
            await body.click()
            await random_delay(0.5, 1.0)

            # 클립보드를 통한 붙여넣기 (서식 보존 + 속도 향상)
            await self.page.evaluate(
                f"navigator.clipboard.writeText({repr(content)})"
            )
            await random_delay(0.2, 0.4)
            await self.page.keyboard.press("Meta+v")  # macOS: Cmd+V
            await random_delay(0.5, 1.0)
        except Exception:
            # 폴백: 직접 타이핑
            try:
                frame_locator = self.page.frame_locator(SELECTORS["editor_frame"])
                body = frame_locator.locator(SELECTORS["editor_body"]).first
                await body.type(content, delay=30)
            except Exception as e:
                raise RuntimeError(f"본문 입력 실패: {e}\n선택자를 확인하세요: {SELECTORS['editor_frame']}")

    async def _set_category(self, category_name: str):
        """카테고리 선택"""
        try:
            dropdown = self.page.locator(SELECTORS["category_dropdown"])
            if await dropdown.count() > 0:
                await dropdown.click()
                await random_delay(0.3, 0.5)
                # 카테고리 이름으로 항목 선택
                category_option = self.page.locator(f"text='{category_name}'")
                if await category_option.count() > 0:
                    await category_option.first.click()
                    await random_delay(0.3, 0.5)
        except Exception:
            # 카테고리 설정 실패는 치명적이지 않으므로 경고만 출력
            print(f"[경고] 카테고리 '{category_name}' 설정 실패. 기본 카테고리로 발행됩니다.")

    async def _input_tags(self, tags: list[str]):
        """태그 입력"""
        try:
            tag_input = self.page.locator(SELECTORS["tag_input"])
            if await tag_input.count() > 0:
                for tag in tags[:10]:  # 네이버 블로그 태그 최대 10개
                    await tag_input.fill(tag)
                    await self.page.keyboard.press("Enter")
                    await random_delay(0.2, 0.4)
        except Exception:
            print(f"[경고] 태그 입력 실패. 태그 없이 발행됩니다.")

    async def _publish(self) -> str | None:
        """발행 버튼 클릭 및 URL 반환"""
        try:
            publish_btn = self.page.locator(SELECTORS["publish_btn"])
            await publish_btn.wait_for(timeout=5000)
            await publish_btn.click()
            await random_delay(0.5, 1.0)

            # 발행 확인 팝업 처리
            confirm = self.page.locator(SELECTORS["publish_confirm"])
            if await confirm.count() > 0:
                await confirm.first.click()
                await random_delay(1.0, 2.0)

            # 발행 후 포스팅 URL 추출
            await self.page.wait_for_load_state("networkidle", timeout=15000)
            current_url = self.page.url
            return current_url if "PostView" in current_url else None
        except Exception as e:
            raise RuntimeError(f"발행 실패: {e}")

    async def _save_draft(self):
        """임시저장"""
        try:
            draft_btn = self.page.locator(SELECTORS["draft_btn"])
            await draft_btn.wait_for(timeout=5000)
            await draft_btn.click()
            await random_delay(1.0, 1.5)
        except Exception as e:
            raise RuntimeError(f"임시저장 실패: {e}")
