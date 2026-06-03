#!/usr/bin/env python3
"""
Markdown → PDF (Playwright Chromium). 이미지/한글/이모지 지원.
사용: python3 build_pdf.py --md BUY_TRADING_DATA.md --out BUY_TRADING_DATA.pdf
"""
import os, sys, argparse, asyncio
from pathlib import Path

CSS = """
<style>
  body{font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:12px;
       line-height:1.5;color:#1a1a1a;padding:24px;max-width:1000px;margin:auto;}
  h1{font-size:22px;border-bottom:2px solid #333;padding-bottom:6px;}
  h2{font-size:16px;margin-top:26px;border-left:4px solid #4a7;padding-left:8px;}
  blockquote{color:#555;border-left:3px solid #ccc;margin:8px 0;padding:2px 12px;background:#f7f7f7;}
  table{border-collapse:collapse;width:100%;margin:8px 0;font-size:11px;}
  th,td{border:1px solid #bbb;padding:4px 7px;text-align:center;}
  th{background:#eef3f0;}
  img{max-width:100%;height:auto;border:1px solid #ddd;margin:6px 0;}
  hr{border:none;border-top:1px solid #ddd;margin:18px 0;}
  code{background:#f0f0f0;padding:1px 4px;border-radius:3px;}
</style>
"""

async def render(html_path, out):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto(f"file://{html_path}", wait_until="networkidle")
        await pg.pdf(path=out, format="A4", print_background=True,
                     margin={"top":"12mm","bottom":"12mm","left":"10mm","right":"10mm"})
        await b.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    try:
        import markdown
    except ImportError:
        sys.exit("❌ pip3 install markdown 필요")
    text = Path(a.md).read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    html = f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{body}</body></html>"
    html_path = str(Path(a.md).resolve().with_suffix(".render.html"))
    Path(html_path).write_text(html, encoding="utf-8")
    asyncio.run(render(html_path, str(Path(a.out).resolve())))
    os.remove(html_path)
    print(f"✓ PDF 생성: {a.out}")

if __name__ == "__main__":
    main()
