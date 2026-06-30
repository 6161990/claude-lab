#!/usr/bin/env python3
"""
StockEasy 밸류에이션 보드 섹터 스크리너 (고밸류/저밸류 종목 발굴)

StockEasy `/api/v1/valuation/data` 원본(전 종목 PER 보드)을 인증 없이 받아,
지정한 대분류(섹터)에서 PER 순으로 종목을 정렬해 리포트를 만든다.

⚠️ 원칙: 값을 가공·추정하지 않는다. StockEasy 제공 PER/시총을 그대로 정렬·필터만 한다.
       (필터는 '선택'일 뿐 수치 변형이 아님. 환산 표기 외 계산 없음.)

사용:
  python3 screen_valuation.py [옵션]
옵션:
  --sectors 방산 소비재 전력/에너지 바이오 반도체   # 대분류(생략 시 전체)
  --per   {trailing|y2025|e2026|e2027|e2028}        # 정렬 기준 PER (기본 trailing=직전4분기)
  --order {high|low}                                 # high=고밸류순(기본), low=저밸류순
  --min-cap 1000                                     # 최소 시총(억, 기본 1000)
  --top 12                                           # 섹터당 표기 수(기본 12)
  --out reports/                                      # 리포트 저장 경로(기본 reports/)
  --no-report                                         # 파일 저장 없이 출력만

대분류 목록(2026.06 기준): 바이오, IT/플랫폼, 소비재, 화학/소재, 반도체, 자동차,
  인프라, 기계, K-컬처, 금융, 2차전지, 전력/에너지, 지주사, 조선/해운, 방산

stdlib만 사용(urllib).
"""
import os, sys, json, argparse, urllib.request, urllib.error

BASE = "https://stockeasy.intellio.kr/stockdata"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockeasy.intellio.kr/", "Accept": "application/json"}

PER_FIELD = {
    "trailing": "직전_4분기_PER",
    "y2025": "2025_PER",
    "e2026": "2026(E)_PER",
    "e2027": "2027(E)_PER",
    "e2028": "2028(E)_PER",
}
PER_LABEL = {
    "trailing": "직전4분기 PER", "y2025": "2025 PER",
    "e2026": "2026(E) PER", "e2027": "2027(E) PER", "e2028": "2028(E) PER",
}


def get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def num(v):
    return v if isinstance(v, (int, float)) else None


def fmt(v):
    return f"{v:.1f}" if isinstance(v, (int, float)) else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sectors", nargs="*", default=None)
    ap.add_argument("--per", choices=list(PER_FIELD), default="trailing")
    ap.add_argument("--order", choices=["high", "low"], default="high")
    ap.add_argument("--min-cap", type=float, default=1000.0, help="억 단위")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out", default="reports")
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args()

    field = PER_FIELD[args.per]
    min_cap = args.min_cap * 1e8
    payload = get("/api/v1/valuation/data")
    rows = payload["data"]["data"]
    date = payload["data"]["date"]
    date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    all_sectors = sorted({r.get("대분류") for r in rows.values() if r.get("대분류")})
    sectors = args.sectors or all_sectors
    bad = [s for s in sectors if s not in all_sectors]
    if bad:
        sys.exit(f"❌ 없는 대분류: {bad}\n   사용 가능: {all_sectors}")

    desc_order = (args.order == "high")
    lines = []
    lines.append(f"# {'고' if desc_order else '저'}밸류 스크리닝 — {', '.join(sectors)}\n")
    lines.append(f"> 출처: StockEasy `/api/v1/valuation/data` 원본 (기준일 {date_fmt}). 추정 없음.")
    lines.append(f"> 기준: **{PER_LABEL[args.per]} {'내림차순' if desc_order else '오름차순'}**, "
                 f"시총 ≥ {args.min_cap:,.0f}억, 적자(음수 PER) 제외.")
    lines.append("> 비고: 미래추정 PER(26E)이 직전PER보다 크게 낮으면 = 실적 바닥/회복 기대(일시적 고PER). 둘 다 높으면 = 구조적 고밸류.\n")

    for sec in sectors:
        sel = []
        for code, r in rows.items():
            if r.get("대분류") != sec:
                continue
            p = num(r.get(field))
            cap = r.get("market_cap") or 0
            if p is None or p <= 0 or cap < min_cap:
                continue
            sel.append((p, code, r))
        sel.sort(reverse=desc_order)
        tot = sum(1 for c, r in rows.items() if r.get("대분류") == sec)
        lines.append(f"## {sec}  (전체 {tot} · 조건충족 {len(sel)})\n")
        lines.append(f"| # | 종목(코드) | {PER_LABEL[args.per]} | 2025 PER | 26E PER | 시총(억) | RS | 중분류 |")
        lines.append("|---|---|--:|--:|--:|--:|--:|---|")
        for i, (p, code, r) in enumerate(sel[:args.top], 1):
            cap = r["market_cap"] / 1e8
            lines.append(f"| {i} | {r['name']}({code}) | **{p:.1f}** | "
                         f"{fmt(r.get('2025_PER'))} | {fmt(r.get('2026(E)_PER'))} | "
                         f"{cap:,.0f} | {r.get('RS')} | {r.get('중분류')} |")
        lines.append("")

    report = "\n".join(lines)
    print(report)
    if not args.no_report:
        os.makedirs(args.out, exist_ok=True)
        tag = "고밸류" if desc_order else "저밸류"
        fp = os.path.join(args.out, f"스크리닝_{tag}_{'_'.join(s.replace('/', '') for s in sectors)}.md")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n저장: {fp}")


if __name__ == "__main__":
    main()
