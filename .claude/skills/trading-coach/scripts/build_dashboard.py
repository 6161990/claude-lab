#!/usr/bin/env python3
"""트레이딩 원칙 준수 대시보드 생성 (trading-coach 가시화).

coach_log.json을 읽어 GitHub Pages용 **자체완결 HTML**(외부 의존 0)을 만든다.
- 월별 달력: 일지 적은 날 ✓ + 준수율로 색칠
- 반복 위반 카운터: 같은 원칙을 몇 번 어겼는지 (한 달 뒤 최종확인용)
- 요약: 기록일수 · 평균 준수율 · 무위반 스트릭

이 대시보드는 김민우(네프콘)의 BUY_TRADING_DATA와 무관하다 — 본인 매매일지 기록만 집계한다.

사용:
    python3 build_dashboard.py --log coach_feedback/coach_log.json --out docs/index.html
"""
import argparse
import calendar
import html as _html
import json
import os
import re
from collections import Counter, defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_scorecard import RULE_NAMES  # 룰 ID→이름 단일 출처

WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"]


def _strip_md(s):
    """마크다운 강조(**, `) 제거 + 좌우 공백 정리."""
    return re.sub(r"[*`]", "", s).strip()


def _table_cells(line):
    """| a | b | c | → ['a','b','c'] (양끝 빈칸 제거). 표 행이 아니면 None."""
    if not line.lstrip().startswith("|"):
        return None
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    return parts


def parse_rulebook(path):
    """TRADING_RULES.md를 파싱해 (개인기준[(항목,값)], 카테고리[(제목,[(ID,규칙)])]) 반환.
    룰북이 단일 출처이므로 대시보드는 코드에 규칙을 복제하지 않는다."""
    if not os.path.exists(path):
        return [], []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    criteria, categories = [], []
    section = None          # "criteria" | "rules" | None
    cur_cat = None
    for ln in lines:
        if ln.startswith("## 내 기준"):
            section = "criteria"
            continue
        if ln.startswith("### "):
            section = "rules"
            cur_cat = (_strip_md(ln[4:]), [])
            categories.append(cur_cat)
            continue
        if ln.startswith("#"):          # 다른 ## 섹션 진입
            section = None
            continue
        cells = _table_cells(ln)
        if not cells or len(cells) < 2:
            continue
        c0, c1 = _strip_md(cells[0]), _strip_md(cells[1])
        if not c0 or c0.startswith("-") or c0 in ("항목", "ID"):
            continue                    # 헤더/구분선
        if section == "criteria":
            criteria.append((c0, c1))
        elif section == "rules" and cur_cat is not None and re.match(r"^[A-Z]\d+$", c0):
            cur_cat[1].append((c0, c1))
    return criteria, categories


def color_for(score):
    """준수율 → 색. 결과가 아니라 원칙 준수도를 색으로."""
    if score is None:
        return "#ebedf0"  # 기록은 있으나 채점 불가
    if score >= 80:
        return "#216e39"
    if score >= 60:
        return "#30a14e"
    if score >= 40:
        return "#d4a72c"
    return "#cf222e"


def render_calendar(year, month, log):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    head = "".join(f"<th>{w}</th>" for w in WEEKDAYS)
    rows = []
    for week in cal.monthdayscalendar(year, month):
        cells = []
        for d in week:
            if d == 0:
                cells.append('<td class="empty"></td>')
                continue
            key = f"{year:04d}-{month:02d}-{d:02d}"
            if key in log:
                score = log[key].get("score")
                bg = color_for(score)
                s = f"{score:.0f}%" if score is not None else "—"
                sym = _html.escape(log[key].get("symbol", "") or "")
                sym_html = f'<span class="sym">{sym}</span>' if sym else ""
                tip = f"{key} · 준수율 {s}" + (f" · {sym}" if sym else "")
                cells.append(
                    f'<td class="on" style="background:{bg}" title="{tip}">'
                    f'<span class="dnum">{d} ✓</span>'
                    f'<span class="pct">{s}</span>{sym_html}</td>'
                )
            else:
                cells.append(f'<td class="off"><span class="dnum">{d}</span></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<table class="cal"><caption>{year}년 {month}월</caption>'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="coach_feedback/coach_log.json")
    ap.add_argument("--rules-md", default="TRADING_RULES.md", help="매매원칙 출처")
    ap.add_argument("--out", default="docs/index.html")
    args = ap.parse_args()

    if os.path.exists(args.log):
        with open(args.log, encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = {}

    dates = sorted(log.keys())

    # --- 집계 ---
    fail_counter = Counter()
    fail_dates = defaultdict(list)
    partial_counter = Counter()
    for d in dates:
        for rid, v in log[d].get("verdicts", {}).items():
            if v == "fail":
                fail_counter[rid] += 1
                fail_dates[rid].append(d)
            elif v == "partial":
                partial_counter[rid] += 1

    scores = [log[d]["score"] for d in dates if log[d].get("score") is not None]
    avg = round(sum(scores) / len(scores), 1) if scores else None
    streak = 0
    for d in reversed(dates):
        if Counter(log[d].get("verdicts", {}).values()).get("fail", 0) == 0:
            streak += 1
        else:
            break

    # --- 달력 (데이터가 있는 모든 월) ---
    months = sorted({(int(d[:4]), int(d[5:7])) for d in dates})
    cals = "".join(render_calendar(y, m, log) for y, m in months) or "<p>아직 기록 없음.</p>"

    # --- 반복 위반 카운터 ---
    max_fail = max(fail_counter.values(), default=1)
    viol_rows = []
    for rid, n in fail_counter.most_common():
        name = RULE_NAMES.get(rid, rid)
        w = int(n / max_fail * 100)
        dlist = ", ".join(fail_dates[rid])
        viol_rows.append(
            f'<div class="vrow"><div class="vlabel"><b>{rid}</b> {name}</div>'
            f'<div class="vbar"><div class="vfill" style="width:{w}%">{n}회</div></div>'
            f'<div class="vdates">{dlist}</div></div>'
        )
    viol_html = "".join(viol_rows) or "<p>아직 위반 기록 없음. 🎉</p>"

    total_days = len(dates)
    period = f"{dates[0]} ~ {dates[-1]}" if dates else "—"
    avg_s = f"{avg}%" if avg is not None else "—"

    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>트레이딩 원칙 준수 대시보드</title>
<style>
 :root {{ font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
 body {{ margin:0; background:#0d1117; color:#e6edf3; padding:24px; }}
 h1 {{ font-size:22px; margin:0 0 4px; }}
 .sub {{ color:#8b949e; font-size:13px; margin-bottom:20px; }}
 .cards {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:24px; }}
 .card {{ background:#161b22; border:1px solid #30363d; border-radius:10px; padding:14px 18px; min-width:120px; }}
 .card .big {{ font-size:26px; font-weight:700; }}
 .card .lbl {{ color:#8b949e; font-size:12px; }}
 h2 {{ font-size:16px; border-bottom:1px solid #30363d; padding-bottom:6px; margin:28px 0 14px; }}
 .cals {{ display:flex; gap:18px; flex-wrap:wrap; }}
 table.cal {{ border-collapse:collapse; background:#161b22; border:1px solid #30363d; border-radius:8px; overflow:hidden; }}
 table.cal caption {{ font-weight:700; padding:8px; background:#21262d; }}
 table.cal th {{ color:#8b949e; font-size:11px; padding:4px 0; width:42px; }}
 table.cal td {{ height:46px; width:42px; text-align:center; vertical-align:top; border:1px solid #0d1117; position:relative; }}
 td.empty {{ background:#0d1117; border-color:#0d1117; }}
 td.off .dnum {{ color:#484f58; font-size:12px; }}
 td.on {{ color:#fff; }}
 td.on .dnum {{ font-size:11px; opacity:.85; display:block; }}
 td.on .chk {{ font-size:13px; font-weight:700; }}
 td.on .pct {{ display:block; font-size:10px; opacity:.95; }}
 .legend {{ font-size:12px; color:#8b949e; margin-top:10px; }}
 .legend span {{ display:inline-block; width:12px; height:12px; border-radius:2px; vertical-align:middle; margin:0 4px 0 10px; }}
 .vrow {{ margin-bottom:12px; }}
 .vlabel {{ font-size:13px; margin-bottom:3px; }}
 .vbar {{ background:#21262d; border-radius:5px; overflow:hidden; }}
 .vfill {{ background:#cf222e; color:#fff; font-size:12px; font-weight:700; padding:3px 8px; white-space:nowrap; border-radius:5px; min-width:32px; }}
 .vdates {{ color:#8b949e; font-size:11px; margin-top:2px; }}
 footer {{ color:#484f58; font-size:11px; margin-top:32px; }}
</style></head><body>
 <h1>🥊 트레이딩 원칙 준수 대시보드</h1>
 <div class="sub">본인 매매일지 기록 집계 · 기간 {period} · 결과가 아니라 <b>원칙 준수</b>를 추적</div>

 <div class="cards">
   <div class="card"><div class="big">{total_days}</div><div class="lbl">기록일수</div></div>
   <div class="card"><div class="big">{avg_s}</div><div class="lbl">평균 준수율</div></div>
   <div class="card"><div class="big">🔥 {streak}</div><div class="lbl">무위반 스트릭(일)</div></div>
   <div class="card"><div class="big">{sum(fail_counter.values())}</div><div class="lbl">누적 위반(❌) 수</div></div>
 </div>

 <h2>📅 매매일지 달력 (✓ = 기록한 날)</h2>
 <div class="cals">{cals}</div>
 <div class="legend">준수율:
   <span style="background:#cf222e"></span>~39
   <span style="background:#d4a72c"></span>40–59
   <span style="background:#30a14e"></span>60–79
   <span style="background:#216e39"></span>80+
   <span style="background:#ebedf0"></span>채점불가
 </div>

 <h2>🔁 반복 위반 카운터 — "같은 실수 몇 번?"</h2>
 {viol_html}

 <footer>generated by trading-coach · build_dashboard.py · 김민우(네프콘 BUY_TRADING_DATA)와 무관한 본인 일지 기록</footer>
</body></html>
"""

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] 대시보드 생성 → {args.out} ({total_days}일 기록, 누적 위반 {sum(fail_counter.values())}건)")


if __name__ == "__main__":
    main()
