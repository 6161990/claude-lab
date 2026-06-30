#!/usr/bin/env python3
"""
StockEasy 원본 데이터 수집기 (가치투자 분석용)

StockEasy(stockeasy.intellio.kr) 내부 API(/stockdata)를 인증 없이 호출해
종목의 지표·재무·등급·사업개요·뉴스 '원본 JSON'을 변환 없이 그대로 저장한다.

⚠️ 원칙: 이 스크립트는 어떤 값도 가공/추정/계산하지 않는다. 받은 JSON을 그대로 저장만 한다.
       (WebFetch 마크다운 변환은 숫자를 왜곡하므로 절대 사용하지 말 것.)

사용:
  python3 fetch_stock.py <종목코드 또는 StockEasy URL> [--out data/]
예:
  python3 fetch_stock.py 278470
  python3 fetch_stock.py "https://stockeasy.intellio.kr/stock-analysis?tab=stock_info&code=278470&stockTab=financial"

stdlib만 사용(urllib). 외부 패키지 불필요.
"""
import os, re, sys, json, argparse, urllib.request, urllib.error

BASE = "https://stockeasy.intellio.kr/stockdata"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://stockeasy.intellio.kr/",
    "Accept": "application/json",
}


def extract_code(arg: str) -> str:
    """URL이면 code=XXXXXX 추출, 아니면 6자리 숫자 그대로."""
    m = re.search(r"[?&]code=(\d{6})", arg)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{6})\b", arg)
    if m:
        return m.group(1)
    sys.exit(f"❌ 종목코드를 찾을 수 없습니다: {arg}")


def get(path: str):
    """GET 후 JSON 반환. 실패 시 (None, 상태) 반환."""
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8")), r.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        return None, str(e)


def detect_cs(code: str) -> str:
    """investment.financial_type(C=연결/S=별도)으로 cs 자동 판별. 기본 C."""
    d, _ = get(f"/api/v1/investment/{code}")
    if isinstance(d, dict):
        ft = d.get("financial_type")
        if ft in ("C", "S"):
            return ft
    return "C"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="종목코드 또는 StockEasy URL")
    ap.add_argument("--out", default="data", help="저장 루트 (기본 data/)")
    args = ap.parse_args()

    code = extract_code(args.target)
    cs = detect_cs(code)
    outdir = os.path.join(args.out, code)
    os.makedirs(outdir, exist_ok=True)

    # (저장파일명, API 경로) — 받은 원본 JSON을 변환 없이 그대로 저장
    endpoints = [
        ("stock_info",   f"/api/v1/stock/info/{code}"),
        ("investment",   f"/api/v1/investment/{code}"),
        ("quarterly",    f"/api/v1/financial-statements/quarterly/{code}?cs={cs}&limit=12"),
        ("balance_sheet", f"/api/v1/financial-statements/balance-sheet/{code}?cs={cs}&limit=8"),
        ("cash_flow",    f"/api/v1/financial-statements/cash-flow/{code}?cs={cs}&limit=8"),
        ("company",      f"/api/v1/company/{code}"),
        ("news",         f"/api/v1/news/by-stock-code/{code}"),
    ]

    saved = {}
    for name, path in endpoints:
        data, status = get(path)
        if data is None:
            print(f"  ⚠️  {name}: 실패 (status={status})")
            continue
        fp = os.path.join(outdir, f"{name}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        saved[name] = data
        print(f"  ✓ {name}.json")

    # ── 핵심 원본값 요약 (인용 편의용. 가공 아님, API 값 그대로 출력) ──
    print(f"\n===== 종목 {code} (연결/별도: {cs}) =====")
    si = (saved.get("stock_info") or {}).get("data", {})
    if si:
        print(f"종목명   : {si.get('name')}")
        print(f"현재가   : {si.get('cur_prc')}  (등락률 {si.get('flu_rt')})")
        print(f"시가총액 : {si.get('mac')} (억, 원본)")
        print(f"PER {si.get('per')} | EPS {si.get('eps')} | ROE {si.get('roe')} | PBR {si.get('pbr')} | BPS {si.get('bps')}")
    inv = saved.get("investment") or {}
    if inv:
        print(f"\n[가치투자 4축 등급] 기준 {inv.get('base_period')} vs {inv.get('yoy_period')}")
        for key in ("growth", "profitability", "stability", "valuation"):
            c = inv.get(key)
            if c:
                metrics = ", ".join(f"{m['name']}:{m.get('grade','')}" for m in c.get("metrics", []))
                print(f"  - {c.get('category_name')}({c.get('average_grade')}) | {metrics}")
    print(f"\n저장 위치: {outdir}/")
    print("⚠️ 분석 시 위 원본 JSON만 인용할 것. 추정·임의계산 금지.")


if __name__ == "__main__":
    main()
