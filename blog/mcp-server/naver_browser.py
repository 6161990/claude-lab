"""
네이버 블로그 Playwright 브라우저 자동화 모듈

로그인 및 세션 관리를 담당합니다.
최초 실행 시 브라우저 창이 열리며, 2단계 인증이 있는 경우 수동으로 처리해야 합니다.
로그인 성공 후 세션이 파일로 저장되어 이후 자동 재사용됩니다.
"""

import os
import json
import asyncio
import random
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

load_dotenv()

NAVER_ID = os.getenv("NAVER_ID", "")
NAVER_PASSWORD = os.getenv("NAVER_PASSWORD", "")
BLOG_ID = os.getenv("NAVER_BLOG_ID", "kong__home")
SESSION_PATH = os.getenv("NAVER_SESSION_PATH", ".naver_session.json")

NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?mode=form"
NAVER_HOME_URL = "https://www.naver.com"
BLOG_BASE_URL = f"https://blog.naver.com/{BLOG_ID}"
BLOG_WRITE_URL = f"https://blog.naver.com/PostWriteForm.naver?blogId={BLOG_ID}"


async def random_delay(min_sec: float = 0.5, max_sec: float = 1.5):
    """자연스러운 사람처럼 보이기 위한 랜덤 지연"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


class NaverBlogBrowser:
    """네이버 블로그 Playwright 브라우저 컨텍스트 매니저"""

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    async def __aenter__(self) -> "NaverBlogBrowser":
        self._playwright = await async_playwright().start()

        # headless=False: 네이버 봇 감지 우회 + 2단계 인증 수동 처리 가능
        self._browser = await self._playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        session_file = Path(SESSION_PATH)

        if session_file.exists():
            # 저장된 세션 재사용
            self._context = await self._browser.new_context(
                storage_state=SESSION_PATH,
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )
        else:
            self._context = await self._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )

        self.page = await self._context.new_page()

        # 자동화 감지 방지: navigator.webdriver 속성 숨기기
        await self.page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        await self._ensure_logged_in()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _ensure_logged_in(self):
        """로그인 상태 확인 및 필요 시 로그인 수행"""
        await self.page.goto(NAVER_HOME_URL)
        await random_delay()

        # 로그인 여부 확인: 로그인 상태면 사용자 닉네임이 표시됨
        is_logged_in = await self.page.locator(".MyView-module__link_login___HpHMW").count() == 0

        if not is_logged_in:
            await self._login()

    async def _login(self):
        """네이버 로그인 자동화

        JavaScript evaluate를 통해 input에 값을 직접 설정합니다.
        (키 입력 이벤트 대신 JS 주입으로 봇 감지 우회)

        2단계 인증이 발생하면 사용자가 수동으로 처리해야 합니다.
        로그인 완료 후 세션 파일이 저장됩니다.
        """
        await self.page.goto(NAVER_LOGIN_URL)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # JS로 ID/PW 입력 (키로거 우회)
        await self.page.evaluate(
            f"document.getElementById('id').value = '{NAVER_ID}'"
        )
        await random_delay(0.3, 0.7)
        await self.page.evaluate(
            f"document.getElementById('pw').value = '{NAVER_PASSWORD}'"
        )
        await random_delay(0.5, 1.0)

        await self.page.click(".btn_login")

        # 로그인 완료 대기 (2단계 인증 포함 최대 60초)
        try:
            await self.page.wait_for_url(NAVER_HOME_URL, timeout=60000)
        except Exception:
            # 2단계 인증 등 추가 처리가 필요한 경우: 사용자가 수동으로 완료할 때까지 대기
            print("[안내] 2단계 인증 또는 추가 확인이 필요합니다. 브라우저에서 직접 완료해 주세요.")
            await self.page.wait_for_url(NAVER_HOME_URL, timeout=120000)

        # 세션 저장
        await self._context.storage_state(path=SESSION_PATH)
        print(f"[완료] 로그인 성공. 세션이 {SESSION_PATH}에 저장되었습니다.")

    async def get_categories(self) -> list[dict]:
        """블로그 카테고리 목록 반환"""
        await self.page.goto(BLOG_BASE_URL)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # iframe 내부 카테고리 목록 추출
        frame = self.page.frame("mainFrame") or self.page.main_frame
        categories = await frame.eval_on_selector_all(
            ".category_item a",
            "els => els.map(el => ({name: el.textContent.trim(), href: el.href}))",
        )
        return categories

    async def list_drafts(self) -> list[dict]:
        """임시저장 포스팅 목록 반환"""
        drafts_url = (
            f"https://blog.naver.com/PostTempList.naver?blogId={BLOG_ID}"
        )
        await self.page.goto(drafts_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        frame = self.page.frame("mainFrame") or self.page.main_frame
        drafts = await frame.eval_on_selector_all(
            ".temp_list_item",
            "els => els.map(el => ({title: el.querySelector('.title')?.textContent?.trim() || '(제목 없음)', date: el.querySelector('.date')?.textContent?.trim() || ''}))",
        )
        return drafts
