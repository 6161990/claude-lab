#!/usr/bin/env python3
"""
네프콘 매매일지 URL들에서 이미지 수집.
사용: python3 download_images.py --urls URL1 URL2 ... --out charts/
      python3 download_images.py --urls-file urls.txt --out charts/
의존: blog/nepcon-mcp/nepcon_browser.py (NEPCON_MCP_DIR 환경변수로 경로 지정 가능)
"""
import os, sys, json, asyncio, argparse
from pathlib import Path

def find_mcp_dir():
    cand = os.getenv("NEPCON_MCP_DIR")
    if cand and Path(cand).exists():
        return cand
    # 현재 경로에서 위로 올라가며 탐색
    p = Path.cwd()
    for base in [p, *p.parents]:
        d = base / "blog" / "nepcon-mcp"
        if (d / "nepcon_browser.py").exists():
            return str(d)
    sys.exit("❌ nepcon_browser.py를 찾지 못함. NEPCON_MCP_DIR 환경변수로 경로 지정.")

async def run(urls, out):
    sys.path.insert(0, find_mcp_dir())
    from nepcon_browser import NaverNepconBrowser
    Path(out).mkdir(parents=True, exist_ok=True)
    manifest = []
    async with NaverNepconBrowser() as br:
        for i, url in enumerate(urls, 1):
            try:
                post = await br.read_nepcon_post(url, include_images=True)
                date = post.get("date", f"post{i}")
                imgs = post.get("images", [])
                print(f"[{i}/{len(urls)}] {date}: {len(imgs)}개")
                tag = date.replace('.', '').replace(' ', '_').replace(':', '')
                for j, im in enumerate(imgs, 1):
                    try:
                        await br.page.goto(im.get("src", ""))
                        shot = await br.page.screenshot()
                        fn = f"{out.rstrip('/')}/chart_{tag}_{j}.png"
                        with open(fn, "wb") as f:
                            f.write(shot)
                        manifest.append({"date": date, "url": url, "n": j, "file": fn})
                    except Exception as e:
                        print(f"   ✗ img{j}: {str(e)[:50]}")
                print(f"   ✓ {len(imgs)}장 저장")
            except Exception as e:
                print(f"[{i}] ✗ {str(e)[:80]}")
    with open(f"{out.rstrip('/')}/image_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 총 {len(manifest)}장 → {out}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", nargs="*", default=[])
    ap.add_argument("--urls-file")
    ap.add_argument("--out", default="charts/")
    a = ap.parse_args()
    urls = list(a.urls)
    if a.urls_file:
        urls += [l.strip() for l in open(a.urls_file) if l.strip() and not l.startswith("#")]
    if not urls:
        sys.exit("❌ --urls 또는 --urls-file 필요")
    asyncio.run(run(urls, a.out))

if __name__ == "__main__":
    main()
