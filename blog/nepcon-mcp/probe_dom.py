"""네프콘 글 상세 페이지 DOM 구조 조사용 임시 스크립트"""
import sys, json, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from nepcon_browser import NaverNepconBrowser


async def main():
    url = sys.argv[1]
    async with NaverNepconBrowser() as b:
        await b.page.goto(url)
        await b.page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        info = await b.page.evaluate(
            """() => {
                const out = {title_candidates: [], body_candidates: []};
                // 제목 후보
                for (const sel of ['h1','h2','.viewer_title_content','.content_head__title',
                                   '[class*="title"]','meta[property="og:title"]']) {
                    const el = document.querySelector(sel);
                    if (el) out.title_candidates.push({sel, text: (el.content||el.textContent||'').trim().slice(0,120)});
                }
                // 본문 후보: 텍스트 길이 큰 컨테이너 탐색
                const cands = ['.viewer_body','.article_body','[class*="viewer"]','[class*="article"]',
                               '[class*="content_body"]','[class*="se_"]','#viewerContent','article',
                               '.se-main-container','[class*="editor"]'];
                for (const sel of cands) {
                    const els = document.querySelectorAll(sel);
                    els.forEach((el,i) => {
                        const t = (el.innerText||'').trim();
                        if (t.length > 200) out.body_candidates.push({sel:sel+`[${i}]`, len:t.length, sample:t.slice(0,80)});
                    });
                }
                out.body_candidates.sort((a,b)=>b.len-a.len);
                out.body_candidates = out.body_candidates.slice(0,15);
                out.og_title = (document.querySelector('meta[property="og:title"]')||{}).content||'';
                return out;
            }"""
        )
        print(json.dumps(info, ensure_ascii=False, indent=2))


asyncio.run(main())
