"""
네이버 프리미엄콘텐츠(네프콘) Playwright 브라우저 자동화 모듈

로그인 및 세션 관리를 담당합니다.
최초 실행 시 브라우저 창이 열리며, 2단계 인증이 있는 경우 수동으로 처리해야 합니다.
로그인 성공 후 세션이 파일로 저장되어 이후 자동 재사용됩니다.
"""

from __future__ import annotations

import os
import re
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

    async def list_nepcon_posts(self, channel_url: str, limit: int = 20, category_id: str = None) -> list[dict]:
        """네프콘 채널의 게시글 목록 반환

        Args:
            channel_url: 채널 전체 URL (예: https://contents.premium.naver.com/son/stockson/contents)
            limit: 최대 반환 개수 (기본 20)
            category_id: 카테고리 ID (예: 19a8818e0f5000sho) - 선택사항

        Returns:
            [{"title": "...", "date": "...", "url": "...", "author": "..."}, ...] 형태의 리스트
        """
        # categoryId가 있으면 URL에 추가
        if category_id:
            separator = "&" if "?" in channel_url else "?"
            channel_url = f"{channel_url}{separator}categoryId={category_id}"

        await self.page.goto(channel_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # 게시글 링크 추출 (content_text_link 클래스 + 작성자 정보 포함)
        posts = await self.page.evaluate(
            f"""() => {{
                const links = document.querySelectorAll('.content_text_link');
                const posts = [];

                for (let link of links) {{
                    const href = link.href || '';
                    const title = link.textContent?.trim() || '';

                    // 유효한 게시글인지 확인
                    if (!href || !title || href.length < 10) continue;

                    // 작성자 정보 추출 (같은 카드 내에서)
                    let author = '(작성자 미상)';
                    const card = link.closest('[class*="content"]') || link.parentElement;
                    const authorLink = card?.querySelector('.content_author_link, [class*="author"]');
                    if (authorLink) {{
                        author = authorLink.textContent?.trim() || author;
                    }}

                    posts.push({{
                        title: title,
                        url: href,
                        author: author
                    }});

                    if (posts.length >= {limit}) break;
                }}

                return posts;
            }}"""
        )

        return posts

    async def read_nepcon_post(self, post_url: str, include_images: bool = True) -> dict:
        """특정 게시글 전문 읽어오기

        Args:
            post_url: 게시글 URL
            include_images: 이미지 URL 포함 여부

        Returns:
            {"title": "...", "content": "...", "date": "...", "url": "...", "images": [...]} 형태의 딕셔너리
        """
        await self.page.goto(post_url)
        await self.page.wait_for_load_state("networkidle")
        await random_delay()

        # 제목 추출: og:title 메타태그가 가장 깨끗함
        title = await self.page.evaluate(
            "() => (document.querySelector('meta[property=\"og:title\"]')||{}).content || ''"
        )
        if not title:
            # 폴백: 뷰어 제목 영역 첫 줄
            raw = await self.page.text_content(".viewer_title_content") or ""
            title = raw.strip().split("\n")[0].strip()
        title = title.strip() if title else "(제목 없음)"

        # 본문 추출: 스마트에디터 본문 컨테이너(.se-main-container)의 컴포넌트를
        # 문서 순서대로 훑어 텍스트와 이미지를 인라인 마크다운으로 재구성한다.
        content = await self.page.evaluate(
            """() => {
                const root = document.querySelector('.se-main-container');
                if (!root) return '';
                // 순서목록/불릿의 마커(1. 2. · 등)는 CSS 생성물이라 innerText에 안 잡힌다.
                // → 원문과 일치하도록 마커 텍스트를 DOM에 직접 주입한다.
                // 마커는 li 안쪽 첫 문단(<p>)에 인라인 삽입해야 같은 줄에 붙는다.
                // (li에 직접 넣으면 블록 <p>와 문단이 분리돼 번호만 따로 떨어짐)
                root.querySelectorAll('ol').forEach(ol => {
                    let n = parseInt(ol.getAttribute('start') || '1', 10) || 1;
                    ol.querySelectorAll(':scope > li').forEach(li => {
                        const v = parseInt(li.getAttribute('value') || '', 10);
                        if (!isNaN(v)) n = v;
                        (li.querySelector('p, span, div') || li)
                            .insertAdjacentText('afterbegin', n + '. ');
                        n++;
                    });
                });
                root.querySelectorAll('ul').forEach(ul => {
                    ul.querySelectorAll(':scope > li').forEach(li => {
                        (li.querySelector('p, span, div') || li)
                            .insertAdjacentText('afterbegin', '- ');
                    });
                });
                const parts = [];
                const seen = new Set();
                const isTracker = (src) =>
                    /l\\.gif|blank\\.gif|1x1|spacer|\\.gif\\?type=content/i.test(src);
                const comps = root.querySelectorAll('.se-component, .se_component');
                const nodes = comps.length ? comps : [root];
                // 한 컴포넌트에 텍스트와 이미지가 함께 있을 수 있으므로(예: 텍스트 문단에
                // 추적 픽셀 삽입) 배타적으로 처리하지 않고 텍스트·이미지를 각각 수집한다.
                nodes.forEach(c => {
                    const t = (c.innerText || '').replace(/\\u200b/g, '').trim();
                    if (t) parts.push(t);
                    c.querySelectorAll('img').forEach(img => {
                        const src = img.getAttribute('data-src') || img.src || '';
                        if (src && !seen.has(src) && !isTracker(src)) {
                            seen.add(src);
                            parts.push('![' + (img.alt || '').trim() + '](' + src + ')');
                        }
                    });
                    const cap = (c.querySelector('.se-caption, figcaption') || {}).innerText;
                    if (cap && cap.trim()) parts.push('*' + cap.trim() + '*');
                });
                return parts.join('\\n\\n').trim();
            }"""
        )
        if not content:
            # 폴백: 컨테이너 전체 텍스트
            content = (await self.page.evaluate(
                "() => { const e=document.querySelector('.se-main-container'); return e?(e.innerText||'').trim():''; }"
            )).strip()
        content = content or "(본문 없음)"

        # 감사용: 컨테이너 전체 원문 텍스트(마커 주입 반영 상태)
        full_text = await self.page.evaluate(
            "() => { const e=document.querySelector('.se-main-container');"
            " return e ? (e.innerText || '').replace(/\\u200b/g,'') : ''; }"
        )

        # 게시 날짜 추출: 뷰어 제목 영역 텍스트에서 날짜 패턴 파싱
        date = ""
        raw_head = await self.page.text_content(".viewer_title_content") or ""
        m = re.search(r"\d{4}\.\d{2}\.\d{2}\.?(\s*(오전|오후)\s*\d{1,2}:\d{2})?", raw_head)
        if m:
            date = m.group(0).strip()

        # 제목/날짜/이미지 포함 본문만 반환 (그 외 메타는 불필요)
        return {
            "title": title,
            "content": content,
            "date": date,
            "url": post_url,
            "full_text": full_text,
        }

    async def download_image(self, url: str) -> bytes | None:
        """브라우저 컨텍스트(쿠키/리퍼러 포함)로 이미지 바이트 다운로드"""
        try:
            resp = await self.page.context.request.get(url)
            if resp.ok:
                return await resp.body()
        except Exception:
            pass
        return None

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
