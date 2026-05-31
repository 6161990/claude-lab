"""
네이버 프리미엄콘텐츠(네프콘) Playwright 브라우저 자동화 모듈

로그인 및 세션 관리를 담당합니다.
최초 실행 시 브라우저 창이 열리며, 2단계 인증이 있는 경우 수동으로 처리해야 합니다.
로그인 성공 후 세션이 파일로 저장되어 이후 자동 재사용됩니다.
"""

import os
import json
import asyncio
import random
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

load_dotenv()

NAVER_ID = os.getenv("NEPCON_NAVER_ID", "")
NAVER_PASSWORD = os.getenv("NEPCON_NAVER_PASSWORD", "")
SESSION_PATH = os.getenv("NEPCON_SESSION_PATH", ".nepcon_session.json")
HEADLESS = os.getenv("NEPCON_HEADLESS", "false").lower() != "false"

NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?mode=form"
NAVER_HOME_URL = "https://www.naver.com"
NEPCON_URL = "https://contents.premium.naver.com/"


async def random_delay(min_sec: float = 0.5, max_sec: float = 1.5):
    """자연스러운 사람처럼 보이기 위한 랜덤 지연"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


class NaverNepconBrowser:
    """네이버 프리미엄콘텐츠 Playwright 브라우저 컨텍스트 매니저"""

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    async def __aenter__(self) -> "NaverNepconBrowser":
        self._playwright = await async_playwright().start()

        # headless 모드: 기본값은 False (봇 감지 우회 + 2단계 인증 수동 처리)
        # 환경변수 NEPCON_HEADLESS=true로 headless 모드 활성화
        self._browser = await self._playwright.chromium.launch(
            headless=HEADLESS,
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
        print("[로그인] 시작...")
        await self.page.goto(NAVER_LOGIN_URL)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()
        print("[로그인] 로그인 페이지 로드 완료")

        try:
            # JS로 ID/PW 입력 (키로거 우회)
            await self.page.evaluate(
                f"document.getElementById('id').value = '{NAVER_ID}'"
            )
            print("[로그인] ID 입력 완료")
            await random_delay(0.3, 0.7)
            await self.page.evaluate(
                f"document.getElementById('pw').value = '{NAVER_PASSWORD}'"
            )
            print("[로그인] PW 입력 완료")
            await random_delay(0.5, 1.0)

            await self.page.click(".btn_login")
            print("[로그인] 로그인 버튼 클릭 완료")

            # 로그인 완료 대기
            print("[로그인] 로그인 완료 대기 중... (최대 180초)")
            await self.page.wait_for_url(lambda url: "naver.com" in url, timeout=180000)
            print("[로그인] 로그인 성공!")

        except Exception as e:
            print(f"[로그인] 예외 발생: {str(e)}")
            print("[안내] 브라우저에서 수동으로 로그인을 완료해 주세요.")
            print("[안내] 사용자가 /naver.com으로 이동할 때까지 대기합니다...")
            await self.page.wait_for_url(lambda url: "naver.com" in url, timeout=300000)

        # 세션 저장
        print("[세션] 세션 저장 중...")
        await self._context.storage_state(path=SESSION_PATH)
        print(f"[완료] 로그인 성공. 세션이 {SESSION_PATH}에 저장되었습니다.")

    async def list_nepcon_posts(self, channel_url: str, limit: int = 20) -> list[dict]:
        """네프콘 채널의 게시글 목록 반환

        Args:
            channel_url: 채널 전체 URL (예: https://contents.premium.naver.com/son/stockson/contents)
            limit: 최대 반환 개수 (기본 20)

        Returns:
            [{"title": "...", "date": "...", "url": "..."}, ...] 형태의 리스트
        """
        await self.page.goto(channel_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # 게시글 링크 추출 (content_text_link 클래스 사용)
        posts = await self.page.evaluate(
            f"""() => {{
                const links = document.querySelectorAll('.content_text_link');
                const posts = [];

                for (let link of links) {{
                    const href = link.href || '';
                    const title = link.textContent?.trim() || '';

                    // 유효한 게시글인지 확인
                    if (!href || !title || href.length < 10) continue;

                    posts.push({{
                        title: title,
                        url: href
                    }});

                    if (posts.length >= {limit}) break;
                }}

                return posts;
            }}"""
        )

        return posts

    async def read_nepcon_post(self, post_url: str) -> dict:
        """특정 게시글 전문 읽어오기

        Args:
            post_url: 게시글 URL

        Returns:
            {"title": "...", "content": "...", "date": "...", "url": "..."} 형태의 딕셔너리
        """
        await self.page.goto(post_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # 제목 추출 (다양한 선택자 시도)
        title = None
        for selector in [".content_head__title", "h1", "[class*='title']"]:
            title = await self.page.text_content(selector)
            if title:
                break
        title = title.strip() if title else "(제목 없음)"

        # 본문 추출 (다양한 선택자 시도)
        content = None
        for selector in [".content_main__body", ".article_body", "[class*='content']", "article"]:
            content_elem = await self.page.query_selector(selector)
            if content_elem:
                content = await content_elem.text_content()
                break
        content = content.strip() if content else "(본문 없음)"

        # 게시 날짜 추출 (다양한 선택자 시도)
        date = None
        for selector in [".content_head__info", ".article_info", "time", "[class*='date']"]:
            date = await self.page.text_content(selector)
            if date:
                break
        date = date.strip() if date else ""

        return {
            "title": title,
            "content": content,
            "date": date,
            "url": post_url
        }

    async def search_nepcon_posts(self, channel_url: str, keyword: str) -> list[dict]:
        """채널 내 키워드 검색

        Args:
            channel_url: 채널 URL
            keyword: 검색 키워드

        Returns:
            검색 결과 게시글 목록
        """
        # URL에 쿼리 파라미터 추가
        separator = "&" if "?" in channel_url else "?"
        search_url = f"{channel_url}{separator}search={keyword}"

        await self.page.goto(search_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # 검색 결과 추출
        posts = await self.page.eval_on_selector_all(
            "a[href*='/contents.premium.naver.com/']",
            """els => els.map(el => ({
                title: el.textContent?.trim() || '(제목 없음)',
                url: el.href
            })).filter(p => p.title && p.title !== '(제목 없음)')"""
        )
        return posts
