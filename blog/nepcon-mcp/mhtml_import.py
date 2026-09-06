"""
바탕화면 등에 저장된 .mhtml(웹페이지 통째 저장) 매매일지를 아카이브로 변환.

유료 콘텐츠라 서버에서 못 받는 최근 글을, 사용자가 접근 권한 있을 때 저장해 둔
MHTML 파일에서 전체 본문+이미지를 추출해 우리 표준 HTML(자체포함)로 만든다.
기존 아카이브에 이미 있는 글(파일명 기준)은 건너뛴다.

사용법:
  /usr/bin/python3 mhtml_import.py "<mhtml폴더>" --author "트레이더김씨" --out docs/nepcon
"""

from __future__ import annotations

import sys
import re
import email
import asyncio
import argparse
from email import policy
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent))
from archive_channel import (
    safe_name, render_html, build_index, IMG_MD, _img_mime, EXTRACT_JS
)


def parse_mhtml(path: Path):
    """MHTML → (본문 HTML, {정규화URL: (bytes, subtype)}) 반환"""
    msg = email.message_from_binary_file(open(path, "rb"), policy=policy.default)
    html = None
    images = {}
    for p in msg.walk():
        ct = p.get_content_type()
        if ct == "text/html" and html is None:
            raw = p.get_payload(decode=True)
            html = raw.decode(p.get_content_charset() or "utf-8", "replace")
        elif ct.startswith("image/"):
            loc = (p.get("Content-Location") or "").strip()
            data = p.get_payload(decode=True)
            if loc and data:
                sub = ct.split("/", 1)[1]
                images[loc] = (data, sub)
                images[loc.split("?")[0]] = (data, sub)  # 쿼리 제거 키도 등록
    return html, images


def img_lookup(url: str, images: dict):
    """content의 이미지 URL로 MHTML 내부 바이트 찾기"""
    if url in images:
        return images[url]
    base = url.split("?")[0]
    if base in images:
        return images[base]
    return None


async def import_folder(folder: Path, author: str, out_root: Path):
    author_root = out_root / safe_name(author)
    html_dir = author_root / "html"
    img_dir = author_root / "images"
    for d in (out_root, author_root, html_dir, img_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 기존 아카이브 파일명(중복 방지 seed)
    used_bases = {f.stem for f in html_dir.glob("*.html")}

    files = sorted(folder.rglob("*.mhtml"))
    print(f"MHTML {len(files)}개 발견", file=sys.stderr)

    added, skipped, failed = [], [], []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        for i, mf in enumerate(files, 1):
            try:
                html, images = parse_mhtml(mf)
                if not html:
                    failed.append((mf.name, "HTML 파트 없음")); continue

                await page.set_content(html, wait_until="domcontentloaded")

                # 제목: og:title
                title = await page.evaluate(
                    "() => (document.querySelector('meta[property=\"og:title\"]')||{}).content || ''"
                )
                if not title:
                    raw = await page.evaluate(
                        "() => { const e=document.querySelector('.viewer_title_content');"
                        " return e?e.textContent.trim().split('\\n')[0].trim():''; }"
                    )
                    title = raw or mf.stem
                title = title.strip()

                # 본문: 기존과 동일한 추출 로직
                content = await page.evaluate(EXTRACT_JS)
                if not content or len(re.sub(r"\s", "", IMG_MD.sub("", content))) < 5:
                    failed.append((mf.name, "본문 비어있음(권한없이 저장?)")); continue

                # 날짜
                date = await page.evaluate(
                    "() => { const e=document.querySelector('.viewer_title_content');"
                    " if(!e) return ''; const m=(e.textContent||'')"
                    ".match(/\\d{4}\\.\\d{2}\\.\\d{2}\\.?(\\s*(오전|오후)\\s*\\d{1,2}:\\d{2})?/);"
                    " return m?m[0].trim():''; }"
                )
                # 연도 접두사 (제목에 연도 없고 2026이 아니면)
                ym = re.match(r"(\d{4})", date or "")
                year = ym.group(1) if ym else ""
                if year and year != "2026" and year not in title:
                    title = f"{year}년 {title}"

                base = safe_name(title)
                if base in used_bases:
                    skipped.append(base); continue

                # 이미지 인라인(MHTML 내부 바이트 → base64)
                import base64, html as htmlmod
                post_img_dir = img_dir / base
                blocks = []
                n = 0
                for block in content.split("\n\n"):
                    block = block.strip()
                    if not block:
                        continue
                    m = IMG_MD.fullmatch(block)
                    if m:
                        found = img_lookup(m.group(2), images)
                        if not found:
                            continue
                        data, sub = found
                        n += 1
                        ext = ".jpg" if sub in ("jpeg", "jpg") else f".{sub}"
                        post_img_dir.mkdir(parents=True, exist_ok=True)
                        (post_img_dir / f"{n:02d}{ext}").write_bytes(data)
                        b64 = base64.b64encode(data).decode("ascii")
                        mime = "image/jpeg" if sub in ("jpeg", "jpg") else f"image/{sub}"
                        blocks.append(
                            f'<p><img alt="{htmlmod.escape(m.group(1))}" '
                            f'src="data:{mime};base64,{b64}"></p>'
                        )
                    else:
                        safe = htmlmod.escape(block).replace("\n", "<br>")
                        blocks.append(f"<p>{safe}</p>")
                body_html = "\n".join(blocks)

                doc = render_html(title, date, body_html)
                (html_dir / f"{base}.html").write_text(doc, encoding="utf-8")
                used_bases.add(base)
                added.append(base)
                print(f"[{i}/{len(files)}] 추가: {base}.html (이미지 {n})", file=sys.stderr)
            except Exception as e:
                failed.append((mf.name, str(e)))
                print(f"[{i}/{len(files)}] 실패: {mf.name} -> {e}", file=sys.stderr)
        await browser.close()

    print("\n===== MHTML 임포트 요약 =====", file=sys.stderr)
    print(f"추가 {len(added)} | 이미 있음(스킵) {len(skipped)} | 실패 {len(failed)}", file=sys.stderr)
    for b in added:
        print(f"  + {b}", file=sys.stderr)
    for name, why in failed:
        print(f"  ! {name}: {why}", file=sys.stderr)
    return added


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--author", required=True)
    ap.add_argument("--out", default="docs/nepcon")
    args = ap.parse_args()
    await import_folder(Path(args.folder), args.author, Path(args.out))
    build_index(Path(args.out))
    print("목록 갱신 완료", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
