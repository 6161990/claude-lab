#!/usr/bin/env python3
"""
targets.json + minute_raw/ → 수치 자동 계산 → report_data.json 병합 → BUY_TRADING_DATA.md 재생성(일자순, 증분)
사용: python3 build_report.py --targets targets.json --raw minute_raw/ --store report_data.json --out BUY_TRADING_DATA.md
targets 스키마: [{"date","name","code","img","buy_time"(HHMM),"markers":[["B","HHMM"],...]}]
"""
import os, re, json, argparse

CPS = ["0930","1000","1030","1100","1130","1200","1300","1400","1500","1520"]

def n(v):
    s = str(v); neg = s.startswith("-"); s = re.sub(r"[^0-9.]", "", s)
    return (-1 if neg else 1) * float(s) if s else 0
def hms(v): return re.sub(r"[^0-9]", "", str(v))[-6:]
def cpm(s): return int(s[:2]) * 60 + int(s[2:])
def near(t): return "0930" if cpm(t) < cpm("0930") else min(CPS, key=lambda c: abs(cpm(c) - cpm(t)))
def addmin(h, d):
    t = max(540, int(h[:2]) * 60 + int(h[2:]) + d); return f"{t // 60:02d}{t % 60:02d}"
def f2(x): return f"{x/10000:.2f}조" if x >= 10000 else f"{x:,.0f}억"
def hm(t): return f"{t[:2]}:{t[2:]}"

def cum_at(rows, hhmm):
    tg = hhmm + "59"; c = 0
    for r in sorted(rows, key=lambda x: hms(x["cntr_tm"])):
        tt = hms(r["cntr_tm"])
        if tt < "090000": continue
        if tt > tg: break
        hi, lo, cl = abs(n(r["high_pric"])), abs(n(r["low_pric"])), abs(n(r["cur_prc"]))
        c += abs(n(r["trde_qty"])) * ((hi + lo + cl) / 3 if hi and lo else cl)
    return c / 1e8

def judge(bi, ai):
    if bi <= 0 and ai > 0: return "🟢선취매"
    if ai > bi * 1.2: return "🟢선취매"
    if bi > ai * 1.2: return "🔴추격매"
    return "⚪중립"

def compute(t, rawdir):
    date = t["date"].replace("-", ""); code = t["code"]
    rows = json.load(open(f"{rawdir.rstrip('/')}/{date}_{code}.json", encoding="utf-8"))
    buy = t["buy_time"]
    curve = [round(cum_at(rows, c), 0) for c in CPS]
    prog_t = [addmin(buy, d) for d in (-5, -4, -3, -2, -1, 0)]
    prog = [round(cum_at(rows, x), 0) for x in prog_t]
    before = prog[5] - prog[0]
    after = round(cum_at(rows, addmin(buy, 5)), 0) - prog[5]
    return {**t, "curve": curve, "prog_t": prog_t, "prog": prog,
            "atbuy": prog[5], "before5": before, "after5": after, "judge": judge(before, after)}

def render(store):
    items = sorted(store.values(), key=lambda x: (x["date"], x.get("buy_time", "")))
    L = ["# 트레이더 매매 — 종목별 거래대금 (키움 분봉 실측)\n"]
    L.append("> 거래대금 = 해당일 **09:00 개장부터 누적**(키움 ka10080 1분봉, 억원).")
    L.append("> 매수/매도 시각=차트 마커 판독(±2~3분). 🔴매수 🔵매도.")
    L.append("> **선취매**=매수 후 더 터짐 / **추격매**=매수 전 이미 터짐.\n")
    L.append("## 📊 한눈에 보기 (전 종목)\n")
    L.append("| 일자 | 종목 | 매수시각 | 매수 시점 누적 | 직전 5분 증가 | 매수 후 5분 증가 | 판단 |")
    L.append("|---|---|---|---|---|---|---|")
    for x in items:
        L.append(f"| {x['date'][5:]} | {x['name']} | {hm(x['buy_time'])} | {f2(x['atbuy'])} | "
                 f"+{x['before5']:,.0f}억 | +{x['after5']:,.0f}억 | {x['judge']} |")
    L.append("\n---\n")
    for x in items:
        L.append(f"## {x['date']} · {x['name']} ({x['code']})\n")
        L.append(f"![{x['name']} {x['date']}]({x['img']})\n")
        pt, pv = x["prog_t"], x["prog"]
        labs = ["-5분","-4분","-3분","-2분","-1분","**매수**"]
        L.append("**① 매수 직전 5분간 누적 거래대금 (가속 확인)**\n")
        L.append("| 시점 | " + " | ".join(f"{labs[i]}<br>{hm(pt[i])}" for i in range(6)) + " |")
        L.append("|---|" + "|".join(["---"] * 6) + "|")
        L.append("| 누적 | " + " | ".join(f"{pv[i]:,.0f}억" for i in range(6)) + " |")
        L.append("| 분당Δ | - | " + " | ".join(f"+{pv[i]-pv[i-1]:,.0f}억" for i in range(1, 6)) + " |\n")
        L.append(f"➡️ **매수 직전 5분 +{x['before5']:,.0f}억  vs  매수 후 5분 +{x['after5']:,.0f}억 → {x['judge']}**\n")
        trow = {c: "" for c in CPS}
        for typ, tm in x["markers"]: trow[near(tm)] += ("🔴" if typ == "B" else "🔵")
        L.append("**② 일중 누적 거래대금 추이 (🔴매수/🔵매도 시점)**\n")
        L.append("| 구분 | " + " | ".join(hm(c) for c in CPS) + " |")
        L.append("|---|" + "|".join(["---"] * len(CPS)) + "|")
        L.append("| 누적(억) | " + " | ".join(f"{v:,.0f}" for v in x["curve"]) + " |")
        L.append("| 매매 | " + " | ".join(trow[c] for c in CPS) + " |\n")
        mk = " / ".join(f"{'🔴매수' if a=='B' else '🔵매도'} {hm(b)}" for a, b in x["markers"])
        L.append(f"매매 시점: {mk}\n\n---\n")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--raw", default="minute_raw/")
    ap.add_argument("--store", default="report_data.json")
    ap.add_argument("--out", default="BUY_TRADING_DATA.md")
    a = ap.parse_args()
    store = {}
    if os.path.exists(a.store):
        store = {f"{e['date']}_{e['code']}": e for e in json.load(open(a.store, encoding="utf-8"))}
    added = 0
    for t in json.load(open(a.targets, encoding="utf-8")):
        key = f"{t['date']}_{t['code']}"
        try:
            store[key] = compute(t, a.raw); added += 1
        except FileNotFoundError:
            print(f"✗ {key}: 분봉 없음(STEP3 먼저)")
    json.dump(list(store.values()), open(a.store, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(a.out, "w", encoding="utf-8").write(render(store))
    print(f"✓ {added}건 반영 / 누적 {len(store)}종목 → {a.out}")

if __name__ == "__main__":
    main()
