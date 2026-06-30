#!/usr/bin/env python3
"""누적 스코어카드 갱신 (trading-coach STEP 5).

채점(✅/⚠️/❌/➖)은 Claude가 하고, 이 스크립트는 집계·렌더만 담당한다.
같은 날짜를 다시 넣으면 덮어쓴다(증분). coach_log.json 갱신 후 SCORECARD.md 재생성.

사용:
    python3 update_scorecard.py --date 2026-06-30 --rules verdicts.json \
        --note "손절 무계획만 빼면 깔끔" \
        --log coach_feedback/coach_log.json --out coach_feedback/SCORECARD.md

verdicts.json 형식: {"W1":"pass","W2":"partial","T2":"fail","H1":"na", ...}
  - pass=지킴(1점), partial=부분(0.5점), fail=위반(0점), na=해당없음(분모 제외)
"""
import argparse
import json
import os
from collections import Counter

# 룰북 ID → 표시 이름 (TRADING_RULES.md와 일치). 룰북이 바뀌면 여기도 갱신.
RULE_NAMES = {
    "M1": "지수 상황 진단",
    "M2": "지수에 맞는 종목/전략",
    "W1": "RS 강한 종목",
    "W2": "매수 근거 기록",
    "W3": "충동/뇌피셜 금지",
    "T1": "명시적 진입 신호",
    "T2": "추격매 금지(선취매)",
    "T3": "시초 뇌동매수 금지",
    "H1": "손절가 설정(-2%)",
    "H2": "익절 계획",
    "H3": "1회 손실 가드",
    "H4": "칼손절(버티기 금지)",
    "H5": "물타기 금지",
    "H6": "당일 청산",
    "E1": "사전 기록",
    "E2": "욕심 제어",
    "E3": "과정 기록",
}

VERDICT_MARK = {"pass": "✅", "partial": "⚠️", "fail": "❌", "na": "➖"}
VERDICT_SCORE = {"pass": 1.0, "partial": 0.5, "fail": 0.0}  # na는 제외


def compliance_rate(verdicts):
    """준수율(%) 계산. na는 분모에서 제외. 채점 가능 항목이 없으면 None."""
    eligible = [v for v in verdicts.values() if v in VERDICT_SCORE]
    if not eligible:
        return None
    return round(sum(VERDICT_SCORE[v] for v in eligible) / len(eligible) * 100, 1)


def load_log(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_scorecard(log):
    """log: {date: {"verdicts": {...}, "score": float|None, "note": str}}"""
    dates = sorted(log.keys())
    lines = ["# 트레이딩 코치 누적 스코어카드", ""]
    lines.append("> 결과가 아니라 **원칙 준수율**을 추적한다. 채점: ✅지킴 ⚠️부분 ❌위반 ➖해당없음.")
    lines.append("")

    if not dates:
        lines.append("_아직 기록 없음._")
        return "\n".join(lines) + "\n"

    # 1) 일자별 준수율 추이 (최근 14일)
    lines.append("## 일자별 준수율 추이 (최근 14일)")
    lines.append("")
    lines.append("| 날짜 | 준수율 | ✅ | ⚠️ | ❌ | 총평 |")
    lines.append("|---|---|---|---|---|---|")
    for d in dates[-14:]:
        e = log[d]
        vs = e.get("verdicts", {})
        c = Counter(vs.values())
        score = e.get("score")
        score_s = f"{score}%" if score is not None else "—"
        lines.append(
            f"| {d} | {score_s} | {c.get('pass', 0)} | {c.get('partial', 0)} | "
            f"{c.get('fail', 0)} | {e.get('note', '')} |"
        )
    lines.append("")

    # 2) 추세 (최근 vs 직전 평균)
    scored = [(d, log[d]["score"]) for d in dates if log[d].get("score") is not None]
    if len(scored) >= 2:
        last_d, last_s = scored[-1]
        prev = [s for _, s in scored[:-1]]
        prev_avg = round(sum(prev) / len(prev), 1)
        delta = round(last_s - prev_avg, 1)
        arrow = "📈 개선" if delta > 0 else ("📉 악화" if delta < 0 else "➡️ 유지")
        lines.append(
            f"**추세**: 최근({last_d}) {last_s}% vs 직전 평균 {prev_avg}% → {arrow} ({delta:+}%p)"
        )
        lines.append("")

    # 3) 규칙별 누적 위반(❌) 빈도 TOP
    fail_counter = Counter()
    for d in dates:
        for rid, v in log[d].get("verdicts", {}).items():
            if v == "fail":
                fail_counter[rid] += 1
    if fail_counter:
        lines.append("## 가장 자주 깨는 원칙 (누적 ❌)")
        lines.append("")
        lines.append("| 순위 | 규칙 | 위반 횟수 |")
        lines.append("|---|---|---|")
        for i, (rid, n) in enumerate(fail_counter.most_common(5), 1):
            name = RULE_NAMES.get(rid, rid)
            lines.append(f"| {i} | {rid} {name} | {n}회 |")
        lines.append("")

    # 4) 연속 무위반 스트릭 (최근부터 ❌ 0인 날 연속 카운트)
    streak = 0
    for d in reversed(dates):
        if Counter(log[d].get("verdicts", {}).values()).get("fail", 0) == 0:
            streak += 1
        else:
            break
    lines.append(f"## 🔥 무위반 스트릭: {streak}일 연속")
    lines.append("")
    lines.append(f"_총 {len(dates)}일 기록 · 최종 갱신 {dates[-1]}_")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="거래일 YYYY-MM-DD")
    ap.add_argument("--rules", required=True, help="verdicts.json 경로")
    ap.add_argument("--note", default="", help="한 줄 총평")
    ap.add_argument("--log", default="coach_feedback/coach_log.json")
    ap.add_argument("--out", default="coach_feedback/SCORECARD.md")
    args = ap.parse_args()

    with open(args.rules, encoding="utf-8") as f:
        verdicts = json.load(f)
    bad = {v for v in verdicts.values()} - set(VERDICT_MARK)
    if bad:
        raise SystemExit(f"알 수 없는 판정값: {bad} (pass/partial/fail/na 만 허용)")

    log = load_log(args.log)
    log[args.date] = {  # 같은 날짜 덮어쓰기 = 증분
        "verdicts": verdicts,
        "score": compliance_rate(verdicts),
        "note": args.note,
    }

    os.makedirs(os.path.dirname(args.log) or ".", exist_ok=True)
    with open(args.log, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render_scorecard(log))

    score = log[args.date]["score"]
    print(f"[OK] {args.date} 준수율 {score}% 기록 → {args.out}")


if __name__ == "__main__":
    main()
