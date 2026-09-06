"""
네프콘 채널 전체 아카이브 스크립트

지정한 채널(또는 카테고리) URL의 게시글을 무한스크롤 끝까지 수집한 뒤,
각 글의 본문을 읽어 마크다운(.md) 파일로 저장한다.

사용법:
    # 1단계: 목록만 수집(개수 확인)
    /usr/bin/python3 archive_channel.py "<채널URL>" --list-only

    # 2단계: 전체 본문을 md로 아카이빙
    /usr/bin/python3 archive_channel.py "<채널URL>" --out ../nepcon-archive/stockson
"""

import sys
import os
import re
import json
import html
import base64
import asyncio
import argparse
from pathlib import Path
from urllib.parse import quote

# nepcon_browser 모듈 재사용
sys.path.insert(0, str(Path(__file__).parent))
from nepcon_browser import NaverNepconBrowser, random_delay


def safe_name(text: str) -> str:
    """제목을 최대한 그대로 유지하되 파일시스템 금지 문자만 치환"""
    text = text.replace("/", "／").replace(":", "：")  # 경로 구분자만 전각으로 대체
    text = re.sub(r"[\n\r\t]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "untitled"


def _img_ext(url: str) -> str:
    """URL에서 이미지 확장자 추정 (기본 .jpg)"""
    path = url.split("?")[0].lower()
    for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def _img_mime(ext: str) -> str:
    """확장자 → MIME 타입"""
    return {
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")


# URL 안에 괄호가 들어가는 경우(예: 파일명 ...(20251119131126).jpg)가 있어
# 한 줄 전체를 탐욕적으로 잡아 마지막 ')' 까지 URL로 인식한다.
IMG_MD = re.compile(r"!\[([^\]]*)\]\((https?://.+)\)")

# 본문 추출 JS (nepcon_browser.read_nepcon_post와 동일 로직).
# MHTML 임포트 등에서 재사용하기 위해 모듈 상수로 노출한다.
EXTRACT_JS = r"""() => {
    const root = document.querySelector('.se-main-container');
    if (!root) return '';
    root.querySelectorAll('ol').forEach(ol => {
        let n = parseInt(ol.getAttribute('start') || '1', 10) || 1;
        ol.querySelectorAll(':scope > li').forEach(li => {
            const v = parseInt(li.getAttribute('value') || '', 10);
            if (!isNaN(v)) n = v;
            (li.querySelector('p, span, div') || li).insertAdjacentText('afterbegin', n + '. ');
            n++;
        });
    });
    root.querySelectorAll('ul').forEach(ul => {
        ul.querySelectorAll(':scope > li').forEach(li => {
            (li.querySelector('p, span, div') || li).insertAdjacentText('afterbegin', '- ');
        });
    });
    const parts = [];
    const seen = new Set();
    const isTracker = (src) => /l\.gif|blank\.gif|1x1|spacer|\.gif\?type=content/i.test(src);
    const comps = root.querySelectorAll('.se-component, .se_component');
    const nodes = comps.length ? comps : [root];
    nodes.forEach(c => {
        const t = (c.innerText || '').replace(/​/g, '').trim();
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
    return parts.join('\n\n').trim();
}"""


async def build_body_html(browser, content: str, base: str, img_dir: Path):
    """본문(텍스트+이미지 마크다운)을 자체포함 HTML로 변환.

    이미지는 원격에서 내려받아
      1) 원본 파일을 img_dir/<base>/NN.ext 로 저장하고,
      2) 동시에 base64 data URI로 HTML에 인라인 임베드한다.
    → HTML 파일 하나만 전달해도 이미지가 깨지지 않고, 원본도 별도 보관된다.

    반환: (html, 기대이미지수, 저장이미지수)
    """
    blocks_html = []
    post_img_dir = img_dir / base
    n_expected = 0
    n_saved = 0
    for block in content.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        m = IMG_MD.fullmatch(block)
        if m:
            n_expected += 1
            url = m.group(2)
            data = await browser.download_image(url)
            if not data:
                print(f"    이미지 다운로드 실패: {url}", file=sys.stderr)
                continue
            n_saved += 1
            ext = _img_ext(url)
            post_img_dir.mkdir(parents=True, exist_ok=True)
            (post_img_dir / f"{n_saved:02d}{ext}").write_bytes(data)
            b64 = base64.b64encode(data).decode("ascii")
            blocks_html.append(
                f'<p><img alt="{html.escape(m.group(1))}" '
                f'src="data:{_img_mime(ext)};base64,{b64}"></p>'
            )
        else:
            safe = html.escape(block).replace("\n", "<br>")
            blocks_html.append(f"<p>{safe}</p>")
    return "\n".join(blocks_html), n_expected, n_saved


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
         max-width: 800px; margin: 40px auto; padding: 0 16px; line-height: 1.75; color: #222; }}
  h1 {{ font-size: 1.5rem; margin-bottom: .2rem; }}
  .date {{ color: #888; font-size: .9rem; margin-top: 0; }}
  hr {{ border: none; border-top: 1px solid #eee; margin: 1.2rem 0; }}
  img {{ max-width: 100%; height: auto; border-radius: 6px; display: block; margin: .6rem auto; }}
  p {{ margin: .5rem 0; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="date">{date}</p>
<hr>
{body}
</body>
</html>
"""


def render_html(title: str, date: str, body_html: str) -> str:
    return HTML_TEMPLATE.format(
        title=html.escape(title), date=html.escape(date or ""), body=body_html
    )


async def scroll_collect_posts(page, channel_url: str, max_scrolls: int = 100) -> list[dict]:
    """무한스크롤로 채널의 모든 게시글 링크 수집"""
    await page.goto(channel_url)
    await page.wait_for_load_state("networkidle")
    await random_delay()

    prev_count = -1
    stable_rounds = 0
    for i in range(max_scrolls):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.2)
        count = await page.evaluate(
            "() => document.querySelectorAll('.content_text_link').length"
        )
        print(f"[scroll {i+1}] 링크 {count}개", file=sys.stderr)
        if count == prev_count:
            stable_rounds += 1
            if stable_rounds >= 3:  # 3회 연속 변화 없으면 종료
                break
        else:
            stable_rounds = 0
        prev_count = count

    posts = await page.evaluate(
        """() => {
            const links = document.querySelectorAll('.content_text_link');
            const seen = new Set();
            const out = [];
            for (const link of links) {
                const href = link.href || '';
                const title = (link.textContent || '').trim();
                if (!href || !title || seen.has(href)) continue;
                seen.add(href);
                out.push({ title, url: href });
            }
            return out;
        }"""
    )
    return posts


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>네프콘 아카이브</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
         margin: 0; line-height: 1.6; color: #222; background: #fafafa; }}
  .wrap {{ display: flex; align-items: flex-start; }}
  /* 사이드바 */
  .side {{ position: sticky; top: 0; height: 100vh; width: 240px; flex-shrink: 0;
          background: #1f2937; color: #e5e7eb; padding: 20px 14px; overflow-y: auto; }}
  .side h1 {{ font-size: 1.2rem; margin: 0 0 14px; color: #fff; }}
  .side #q {{ width: 100%; padding: 8px 10px; border: none; border-radius: 6px;
             margin-bottom: 14px; font-size: .9rem; }}
  .nav {{ display: flex; justify-content: space-between; align-items: center;
         padding: 8px 10px; border-radius: 6px; color: #cbd5e1; text-decoration: none;
         font-size: .92rem; margin-bottom: 2px; cursor: pointer; }}
  .nav:hover {{ background: #374151; color: #fff; }}
  .nav.active {{ background: #2563eb; color: #fff; }}
  .nav b {{ font-weight: 600; font-size: .8rem; opacity: .8; }}
  /* 본문 */
  .main {{ flex: 1; max-width: 860px; margin: 0 auto; padding: 30px 24px; }}
  .author {{ margin-bottom: 2.5rem; scroll-margin-top: 12px; }}
  .author h2 {{ font-size: 1.25rem; border-bottom: 2px solid #333; padding-bottom: .3rem; }}
  .author h2 .cnt {{ color: #888; font-size: .9rem; font-weight: normal; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: .35rem 0; border-bottom: 1px solid #eee; display: flex; gap: .6rem; }}
  li .d {{ color: #999; font-size: .85rem; min-width: 6.5rem; flex-shrink: 0; }}
  li a {{ color: #1a56db; text-decoration: none; }}
  li a:hover {{ text-decoration: underline; }}
  .empty {{ color: #aaa; padding: .5rem 0; display: none; }}
  @media (max-width: 640px) {{
    .wrap {{ flex-direction: column; }}
    .side {{ position: static; height: auto; width: 100%; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <aside class="side">
    <h1>📁 네프콘 아카이브</h1>
    <input id="q" placeholder="🔍 제목 검색">
    <nav id="nav">
      <a class="nav active" data-t="all">전체 <b>{total}</b></a>
{navlinks}
    </nav>
  </aside>
  <main class="main">
{sections}
  </main>
</div>
<script>
  const navs = [...document.querySelectorAll('.nav')];
  const secs = [...document.querySelectorAll('.author')];
  const q = document.getElementById('q');
  function applyFilter() {{
    const v = q.value.trim().toLowerCase();
    const active = document.querySelector('.nav.active').dataset.t;
    secs.forEach(s => {{
      const onAuthor = (active === 'all' || s.id === active);
      let visible = 0;
      s.querySelectorAll('li').forEach(li => {{
        const hit = !v || li.textContent.toLowerCase().includes(v);
        li.style.display = hit ? '' : 'none';
        if (hit) visible++;
      }});
      s.style.display = onAuthor ? '' : 'none';
      const emp = s.querySelector('.empty');
      if (emp) emp.style.display = (onAuthor && visible === 0) ? 'block' : 'none';
    }});
  }}
  navs.forEach(a => a.addEventListener('click', e => {{
    e.preventDefault();
    navs.forEach(x => x.classList.remove('active'));
    a.classList.add('active');
    applyFilter();
    if (a.dataset.t !== 'all') {{
      const el = document.getElementById(a.dataset.t);
      if (el) el.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }} else {{
      window.scrollTo({{top: 0, behavior: 'smooth'}});
    }}
  }}));
  q.addEventListener('input', applyFilter);
</script>
</body>
</html>
"""


def build_index(out_root: Path):
    """out_root 하위의 각 작성자 폴더(<author>/html/*.html)를 스캔해
    작성자별로 구분된 목록 페이지(index.html)를 생성한다."""
    sections = []
    navlinks = []
    total = 0
    n_authors = 0
    for author_dir in sorted(p for p in out_root.iterdir() if p.is_dir()):
        html_dir = author_dir / "html"
        if not html_dir.is_dir():
            continue
        items = []
        for f in html_dir.glob("*.html"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            mt = re.search(r"<h1>(.*?)</h1>", text, re.S)
            md = re.search(r'<p class="date">(.*?)</p>', text, re.S)
            title = html.unescape(mt.group(1).strip()) if mt else f.stem
            date = html.unescape(md.group(1).strip()) if md else ""
            sk = re.search(r"(\d{4}\.\d{2}\.\d{2})", date)
            sortkey = sk.group(1) if sk else "0000.00.00"
            rel = f"{quote(author_dir.name)}/html/{quote(f.name)}"
            items.append((sortkey, title, date, rel))
        if not items:
            continue
        items.sort(key=lambda x: x[0], reverse=True)
        sec_id = f"a{n_authors}"
        n_authors += 1
        total += len(items)
        name = html.escape(author_dir.name)
        lis = "\n".join(
            f'    <li><span class="d">{html.escape(dt)}</span>'
            f'<a href="{rel}">{html.escape(ti)}</a></li>'
            for _, ti, dt, rel in items
        )
        sections.append(
            f'<section class="author" id="{sec_id}">\n'
            f'  <h2>{name} <span class="cnt">({len(items)}개)</span></h2>\n'
            f'  <ul>\n{lis}\n  </ul>\n'
            f'  <p class="empty">검색 결과가 없습니다.</p>\n</section>'
        )
        navlinks.append(
            f'      <a class="nav" data-t="{sec_id}">{name} <b>{len(items)}</b></a>'
        )
    doc = INDEX_TEMPLATE.format(
        total=total, n_authors=n_authors,
        navlinks="\n".join(navlinks), sections="\n".join(sections)
    )
    (out_root / "index.html").write_text(doc, encoding="utf-8")
    print(f"목록 페이지 생성: {out_root / 'index.html'} (총 {total}개)", file=sys.stderr)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel_url", nargs="?", help="--index-only 시 생략 가능")
    parser.add_argument("--out", default="../nepcon-archive", help="아카이브 루트(docs/nepcon)")
    parser.add_argument("--author", default="트레이더김씨", help="작성자(하위 폴더명)")
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--index-only", action="store_true", help="목록 페이지만 재생성")
    parser.add_argument("--update", action="store_true",
                        help="기존 _index.json에 없는 신규 글만 증분 추가")
    parser.add_argument("--limit", type=int, default=0, help="0이면 전체")
    args = parser.parse_args()

    out_root = Path(args.out)

    # 목록 페이지만 재생성 (스크래핑 없음)
    if args.index_only:
        build_index(out_root)
        return

    # 작성자별 폴더: out_root/<author>/{html,images}
    author_root = out_root / safe_name(args.author)
    html_dir = author_root / "html"
    img_dir = author_root / "images"
    for d in (out_root, author_root, html_dir, img_dir):
        d.mkdir(parents=True, exist_ok=True)

    async with NaverNepconBrowser() as browser:
        posts = await scroll_collect_posts(browser.page, args.channel_url)
        print(f"\n총 {len(posts)}개 게시글 발견", file=sys.stderr)

        if args.list_only:
            for i, p in enumerate(posts, 1):
                print(f"{i:3d}. {p['title']}")
            return

        index_path = author_root / "_index.json"
        used_bases = set()  # 파일명 중복 방지 (같은 제목 글이 여러 개인 경우)

        if args.update:
            # 증분: 기존 목록에 없는 URL만 신규로 선별
            prev = []
            if index_path.exists():
                prev = json.loads(index_path.read_text(encoding="utf-8"))
            prev_urls = {p["url"] for p in prev}
            targets = [p for p in posts if p["url"] not in prev_urls]
            print(f"신규 글 {len(targets)}개 (기존 {len(prev_urls)}개)", file=sys.stderr)
            if not targets:
                print("추가할 신규 글 없음. 최신 상태입니다.", file=sys.stderr)
                return
            # 기존 파일명을 seed 하여 신규 파일과의 충돌 방지
            used_bases = {f.stem for f in html_dir.glob("*.html")}
            # _index.json 갱신: 신규를 앞에 두고 기존 이어붙임
            merged = targets + prev
            index_path.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        else:
            # 전체 재수집
            index_path.write_text(
                json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            targets = posts if args.limit == 0 else posts[: args.limit]

        audit = []  # 감사 로그: (제목, 본문길이, 기대이미지, 저장이미지, 오류)
        for i, p in enumerate(targets, 1):
            try:
                full = await browser.read_nepcon_post(p["url"])
                title = full.get("title") or p["title"]
                # 올해(2026)가 아닌 글은 제목 앞에 연도를 붙여 구분 (예: 2025년 11월21일 ...)
                # 단, 제목에 이미 연도가 들어있으면(예: 2025-01-05) 중복 방지로 생략
                ym = re.match(r"(\d{4})", full.get("date", "") or "")
                year = ym.group(1) if ym else ""
                if year and year != "2026" and year not in title:
                    title = f"{year}년 {title}"
                base = safe_name(title)
                # 동일 제목이 이미 있으면 (2), (3)... 을 붙여 파일 덮어쓰기 방지
                if base in used_bases:
                    k = 2
                    while f"{base} ({k})" in used_bases:
                        k += 1
                    base = f"{base} ({k})"
                used_bases.add(base)
                body_content = full.get("content", "")
                # 본문을 이미지 base64 내장 HTML로 변환 + 원본 이미지는 images/에 저장
                body_html, n_exp, n_saved = await build_body_html(
                    browser, body_content, base, img_dir
                )
                doc = render_html(title, full.get("date", ""), body_html)
                fname = f"{base}.html"
                (html_dir / fname).write_text(doc, encoding="utf-8")
                # 텍스트 누락 감사: 추출 텍스트(이미지 제외) vs 컨테이너 원문 길이 비교
                recon_txt = re.sub(r"\s", "", IMG_MD.sub("", body_content))
                full_txt = re.sub(r"\s", "", full.get("full_text", "") or "")
                coverage = (len(recon_txt) / len(full_txt)) if full_txt else 1.0
                audit.append((base, len(body_content), n_exp, n_saved, "", round(coverage, 3)))
                flags = ""
                if n_exp != n_saved:
                    flags += f"  ⚠ 이미지 {n_saved}/{n_exp}"
                if coverage < 0.97:
                    flags += f"  ⚠ 텍스트누락 {coverage:.0%}"
                print(f"[{i}/{len(targets)}] 저장: {fname}{flags}", file=sys.stderr)
            except Exception as e:
                audit.append((p.get("title", "?"), 0, 0, 0, str(e), 0.0))
                print(f"[{i}/{len(targets)}] 실패: {p['url']} -> {e}", file=sys.stderr)
            await random_delay(0.8, 1.6)

        # 작성자별 폴더 구성 후 전체 목록 페이지 재생성
        build_index(out_root)

        # 감사 리포트 저장 + 요약
        audit_rows = [
            {"title": t, "content_len": cl, "img_expected": ne,
             "img_saved": ns, "error": err, "text_coverage": cov}
            for (t, cl, ne, ns, err, cov) in audit
        ]
        audit_path = author_root / "_audit.json"
        if args.update and audit_path.exists():
            # 증분: 기존 감사 이력 앞에 신규분을 덧붙임
            prev_audit = json.loads(audit_path.read_text(encoding="utf-8"))
            audit_rows = audit_rows + prev_audit
        audit_path.write_text(
            json.dumps(audit_rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        n_total = len(audit)
        n_err = sum(1 for r in audit if r[4])
        n_imgmiss = sum(1 for r in audit if r[2] != r[3])
        n_short = sum(1 for r in audit if not r[4] and r[1] < 50)
        n_txtmiss = sum(1 for r in audit if not r[4] and r[5] < 0.97)
        tot_exp = sum(r[2] for r in audit)
        tot_saved = sum(r[3] for r in audit)
        print("\n===== 감사(AUDIT) 요약 =====", file=sys.stderr)
        print(f"글 {n_total}개 | 오류 {n_err} | 이미지 누락글 {n_imgmiss} | "
              f"본문<50자 {n_short} | 텍스트누락(<97%) {n_txtmiss}", file=sys.stderr)
        print(f"이미지 기대 {tot_exp} / 저장 {tot_saved} (실패 {tot_exp - tot_saved})",
              file=sys.stderr)
        for (t, cl, ne, ns, err, cov) in audit:
            if err:
                print(f"  [오류] {t}: {err}", file=sys.stderr)
            elif ne != ns:
                print(f"  [이미지] {t}: {ns}/{ne}", file=sys.stderr)
            elif cl < 50:
                print(f"  [짧음] {t}: 본문 {cl}자", file=sys.stderr)
            elif cov < 0.97:
                print(f"  [텍스트누락] {t}: {cov:.0%}", file=sys.stderr)
        print(f"\n완료: {author_root.resolve()} + 목록 {out_root/'index.html'}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
