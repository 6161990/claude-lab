#!/usr/bin/env python3
"""
키움 ka10080 1분봉 수집 → minute_raw/<date>_<code>.json
사용: python3 fetch_minute.py --targets targets.json --out minute_raw/
환경변수: KIWOOM_APPKEY, KIWOOM_SECRETKEY, KIWOOM_ENV(real|mock)
"""
import os, re, sys, json, time, argparse
import requests

ENV = os.getenv("KIWOOM_ENV", "real")
HOST = "https://api.kiwoom.com" if ENV == "real" else "https://mockapi.kiwoom.com"
APPKEY = os.getenv("KIWOOM_APPKEY", "")
SECRETKEY = os.getenv("KIWOOM_SECRETKEY", "")
TKEY = "cntr_tm"

def hms8(v): return re.sub(r"[^0-9]", "", str(v))[:8]

def token():
    if not APPKEY or not SECRETKEY:
        sys.exit("❌ KIWOOM_APPKEY/SECRETKEY 환경변수 필요")
    r = requests.post(f"{HOST}/oauth2/token", json={
        "grant_type": "client_credentials", "appkey": APPKEY, "secretkey": SECRETKEY},
        headers={"Content-Type": "application/json;charset=UTF-8"}, timeout=10)
    r.raise_for_status(); d = r.json()
    t = d.get("token") or d.get("access_token")
    if not t: sys.exit(f"❌ 토큰 실패: {d}")
    return t

def fetch(tok, code, base_date, tic="1"):
    url = f"{HOST}/api/dostk/chart"; matched = []; cont, nk, page = "N", "", 0
    while True:
        h = {"Content-Type": "application/json;charset=UTF-8",
             "authorization": f"Bearer {tok}", "api-id": "ka10080"}
        if cont == "Y": h["cont-yn"] = "Y"; h["next-key"] = nk
        r = requests.post(url, headers=h, json={
            "stk_cd": code, "tic_scope": tic, "upd_stkpc_tp": "1"}, timeout=15)
        r.raise_for_status(); d = r.json()
        rows = d.get("chart") or d.get("stk_min_pole_chart_qry") or []
        if not rows: break
        page += 1
        dates = [hms8(x.get(TKEY, "")) for x in rows]
        matched += [x for x in rows if hms8(x.get(TKEY, "")) == base_date]
        mn = min(d for d in dates if d) if any(dates) else "99999999"
        cont = r.headers.get("cont-yn", "N"); nk = r.headers.get("next-key", "")
        if mn < base_date or cont != "Y" or page > 150: break
        time.sleep(0.2)
    return matched

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--out", default="minute_raw/")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tgts = json.load(open(a.targets, encoding="utf-8"))
    seen = set()
    tok = token(); print("✓ 토큰 발급")
    for t in tgts:
        date = t["date"].replace("-", ""); code = t["code"]
        key = (date, code)
        if key in seen: continue
        seen.add(key)
        outf = f"{a.out.rstrip('/')}/{date}_{code}.json"
        if os.path.exists(outf):
            print(f"= {date} {code} 이미 있음(건너뜀)"); continue
        try:
            rows = fetch(tok, code, date)
            json.dump(rows, open(outf, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"✓ {date} {code}: {len(rows)}봉")
        except Exception as e:
            print(f"✗ {date} {code}: {str(e)[:80]}")
        time.sleep(0.3)

if __name__ == "__main__":
    main()
