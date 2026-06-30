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
import math
import os
import re
from collections import Counter, defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_scorecard import RULE_NAMES  # 룰 ID→이름 단일 출처

WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"]

# 규칙 ID 앞글자 → 한글 카테고리 (영문 약자 대신 한글 표기용)
CAT_KO = {"M": "지수", "W": "종목", "T": "타이밍", "H": "리스크", "E": "기록"}

# 도넛 세그먼트 색 — 채도 낮춘 차분한 톤 (규칙별 고정 → 월이 바뀌어도 일관)
DONUT_PALETTE = [
    "#5b7c99", "#a07e56", "#7a9e7e", "#9c7a8a", "#c08a5e",
    "#6d8a96", "#8a7ca8", "#b0846f", "#7f9183", "#94789a",
    "#8c9bb0", "#a8906a", "#6f8f88", "#9e8090", "#b09a72",
]
_DSIZE, _DR, _DSW = 160, 58, 26
_DCX = _DCY = _DSIZE / 2


def ko_label(rid):
    """W2 → '종목 · 매수 근거…' 식 한글 라벨. 약자 노출 안 함."""
    return RULE_NAMES.get(rid, rid)


def render_donut(title, counter, color_of):
    """단일 도넛(SVG) + 범례. counter: {rule_id: count}. 월별로 재사용."""
    total = sum(counter.values())
    if total == 0:
        return (f'<div class="donut-box"><div class="dtitle">{_html.escape(title)}</div>'
                f'<p class="ok">위반 없음</p></div>')
    circ = 2 * math.pi * _DR
    segs, legend, acc = [], [], 0.0
    for rid, n in counter.most_common():
        frac = n / total
        seg = frac * circ
        color = color_of(rid)
        name = _html.escape(ko_label(rid))
        segs.append(
            f'<circle cx="{_DCX}" cy="{_DCY}" r="{_DR}" fill="none" stroke="{color}" '
            f'stroke-width="{_DSW}" stroke-dasharray="{seg:.2f} {circ - seg:.2f}" '
            f'stroke-dashoffset="{-acc:.2f}" transform="rotate(-90 {_DCX} {_DCY})">'
            f'<title>{name} {n}회 ({frac * 100:.0f}%)</title></circle>'
        )
        acc += seg
        legend.append(
            f'<div class="lgi"><span class="sw" style="background:{color}"></span>'
            f'{name} <b>{n}</b> <span class="lgp">{frac * 100:.0f}%</span></div>'
        )
    svg = (
        f'<svg viewBox="0 0 {_DSIZE} {_DSIZE}" width="160" height="160">{"".join(segs)}'
        f'<text x="{_DCX}" y="{_DCY - 1}" text-anchor="middle" class="dcenter">{total}</text>'
        f'<text x="{_DCX}" y="{_DCY + 16}" text-anchor="middle" class="dcsub">위반</text></svg>'
    )
    return (f'<div class="donut-box"><div class="dtitle">{_html.escape(title)}</div>'
            f'<div class="donut">{svg}<div class="legend2">{"".join(legend)}</div></div></div>')


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
    """TRADING_RULES.md를 파싱해 (개인기준[(항목,값)], 핵심[(ID,규칙)], 기타[(소제목,[(ID,규칙)])]) 반환.
    룰북이 단일 출처이므로 대시보드는 코드에 규칙을 복제하지 않는다."""
    if not os.path.exists(path):
        return [], [], []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    criteria, core, others = [], [], []
    mode = None          # "criteria" | "core" | "others" | None
    cur_sub = None
    for ln in lines:
        if ln.startswith("## 내 기준"):
            mode = "criteria"; continue
        if ln.startswith("## 핵심"):
            mode = "core"; continue
        if ln.startswith("## 기타"):
            mode = "others"; cur_sub = None; continue
        if ln.startswith("## "):
            mode = None; continue
        if ln.startswith("### "):
            if mode == "others":
                cur_sub = (_strip_md(ln[4:]), [])
                others.append(cur_sub)
            continue
        if ln.startswith("#"):          # 문서 제목 등
            mode = None; continue
        cells = _table_cells(ln)
        if not cells or len(cells) < 2:
            continue
        c0, c1 = _strip_md(cells[0]), _strip_md(cells[1])
        if not c0 or c0.startswith("-") or c0 in ("항목", "ID", "기호"):
            continue                    # 헤더/구분선
        if mode == "criteria":
            criteria.append((c0, c1))
        elif mode == "core" and re.match(r"^[A-Z]\d+$", c0):
            core.append((c0, c1))
        elif mode == "others" and cur_sub is not None and re.match(r"^[A-Z]\d+$", c0):
            cur_sub[1].append((c0, c1))
    return criteria, core, others


def _md_inline(s):
    s = _html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def _md_table(rows):
    parsed = [c for c in (_table_cells(r) for r in rows) if c]
    if not parsed:
        return ""
    header, body = parsed[0], parsed[1:]
    if body and all(set(c) <= set("-: ") for c in body[0]):  # 구분선 제거
        body = body[1:]
    th = "".join(f"<th>{_md_inline(c)}</th>" for c in header)
    trs = "".join("<tr>" + "".join(f"<td>{_md_inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f'<table class="md"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


def md_to_html(md):
    """피드백 .md(내가 직접 쓰는 포맷)를 상세 패널용 HTML로 변환."""
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("### "):
            out.append(f"<h4>{_md_inline(ln[4:])}</h4>"); i += 1; continue
        if ln.startswith("## "):
            out.append(f"<h3>{_md_inline(ln[3:])}</h3>"); i += 1; continue
        if ln.startswith("# "):
            out.append(f"<h2>{_md_inline(ln[2:])}</h2>"); i += 1; continue
        if ln.startswith("---"):
            out.append("<hr>"); i += 1; continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(_md_inline(lines[i].lstrip(">").strip())); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        if ln.lstrip().startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(_md_table(tbl)); continue
        if ln.lstrip().startswith(("- ", "* ")):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(("- ", "* ")):
                buf.append(f"<li>{_md_inline(lines[i].lstrip()[2:])}</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        out.append(f"<p>{_md_inline(ln)}</p>"); i += 1
    return "\n".join(out)


def color_for(score):
    """준수율 → 색. 결과가 아니라 원칙 준수도를 색으로."""
    if score is None:
        return "#c4c9d0"  # 기록은 있으나 채점 불가
    if score >= 80:
        return "#3f7d5a"
    if score >= 60:
        return "#6b9b80"
    if score >= 40:
        return "#c4a35a"
    return "#bd7b73"


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
                    f'<td class="on" style="background:{bg}" title="{tip}" '
                    f'data-date="{key}" onclick="showDay(\'{key}\')">'
                    f'<span class="dnum">{d}</span>'
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
    ap.add_argument("--feedback-dir", default="coach_feedback", help="일별 상세 피드백 .md 위치")
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

    # --- 반복 위반: 월별 도넛 그래프 ---
    month_fail = defaultdict(Counter)
    for d in dates:
        ym = d[:7]
        for rid, v in log[d].get("verdicts", {}).items():
            if v == "fail":
                month_fail[ym][rid] += 1
    color_map = {rid: DONUT_PALETTE[i % len(DONUT_PALETTE)]
                 for i, rid in enumerate(sorted(fail_counter))}
    color_of = lambda r: color_map.get(r, "#57606a")
    donuts = "".join(
        render_donut(f"{ym[:4]}년 {int(ym[5:7])}월", month_fail[ym], color_of)
        for ym in sorted(month_fail)
    )
    viol_html = donuts or '<p class="ok">아직 위반 없음</p>'

    # --- 매매원칙 (룰북 파싱) · 핵심 4 규칙만 노출(개인 파라미터 카드는 제외) ---
    _criteria, core, others = parse_rulebook(args.rules_md)
    core_html = "".join(
        f'<div class="core"><span class="cid">{_html.escape(CAT_KO.get(rid[0], rid))}</span>'
        f'<span class="crule">{_html.escape(rule)}</span></div>'
        for rid, rule in core
    )
    principles_html = ""
    if core_html:
        principles_html = (
            '<h2>내 매매원칙 — 핵심 4 (이것만은 매일)</h2>'
            f'<div class="cores">{core_html}</div>'
        )

    # --- 기타 매매원칙 (맨 아래) · 영문 약자 대신 한글명 ---
    other_cats = ""
    for title, rules in others:
        items = "".join(
            f'<li><b>{_html.escape(ko_label(rid))}</b> — {_html.escape(rule)}</li>'
            for rid, rule in rules
        )
        if items:
            other_cats += f'<div class="rcat"><h3>{_html.escape(title)}</h3><ul>{items}</ul></div>'
    other_html = f'<h2>기타 매매원칙</h2><div class="rcats">{other_cats}</div>' if other_cats else ""

    # --- 일별 한 줄 요약 피드 + 날짜 클릭 상세(피드백 .md) ---
    feed_items, detail_blocks = [], []
    for idx, d in enumerate(reversed(dates)):
        e = log[d]
        score = e.get("score")
        s = f"{score:.0f}%" if score is not None else "—"
        bg = color_for(score)
        sym = _html.escape(e.get("symbol", "") or "")
        note = _html.escape(e.get("note", "") or "")
        feed_items.append(
            f'<div class="feed" data-date="{d}" onclick="showDay(\'{d}\')">'
            f'<span class="fbadge" style="background:{bg}">{s}</span>'
            f'<span class="fmeta"><span class="fdate">{d}</span>'
            f'<span class="fsym">{sym}</span></span>'
            f'<span class="fnote">{note}</span></div>'
        )
        fp = os.path.join(args.feedback_dir, f"{d}.md")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as fh:
                body = md_to_html(fh.read())
        else:
            body = f"<p class='muted'>이 날의 상세 피드백 파일이 없습니다 ({d}).</p>"
        show = "block" if idx == 0 else "none"
        detail_blocks.append(f'<div class="detail" id="detail-{d}" style="display:{show}">{body}</div>')
    feed_html = "".join(feed_items) or '<p class="muted">아직 기록 없음.</p>'
    detail_html = "".join(detail_blocks) or '<p class="muted">기록이 쌓이면 여기에 상세 분석이 표시됩니다.</p>'
    latest = dates[-1] if dates else ""

    total_days = len(dates)
    period = f"{dates[0]} ~ {dates[-1]}" if dates else "—"
    avg_s = f"{avg}%" if avg is not None else "—"

    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>트레이딩 원칙 준수 대시보드</title>
<style>
 :root {{ font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
 body {{ margin:0; background:#ffffff; color:#24292f; padding:28px; max-width:1180px; }}
 h1 {{ font-size:21px; margin:0 0 4px; font-weight:700; }}
 .sub {{ color:#57606a; font-size:13px; margin-bottom:22px; }}
 .muted {{ color:#57606a; font-size:13px; }}
 .cards {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:8px; }}
 .card {{ background:#f6f8fa; border:1px solid #d8dee4; border-radius:10px; padding:14px 18px; min-width:118px; }}
 .card .big {{ font-size:25px; font-weight:700; }}
 .card .lbl {{ color:#57606a; font-size:12px; }}
 h2 {{ font-size:15px; border-bottom:1px solid #e1e4e8; padding-bottom:6px; margin:30px 0 14px; font-weight:600; }}
 .board {{ display:flex; gap:28px; align-items:flex-start; flex-wrap:wrap; }}
 .board .col {{ flex:1; min-width:300px; }}
 .cals {{ display:flex; gap:18px; flex-wrap:wrap; }}
 table.cal {{ border-collapse:collapse; background:#fff; border:1px solid #d8dee4; border-radius:8px; overflow:hidden; }}
 table.cal caption {{ font-weight:600; padding:8px; background:#f6f8fa; font-size:13px; }}
 table.cal th {{ color:#8a939d; font-size:11px; padding:4px 0; width:54px; font-weight:500; }}
 table.cal td {{ height:54px; width:54px; text-align:center; vertical-align:top; border:1px solid #eef1f4; position:relative; padding:3px 2px; }}
 td.empty {{ background:#fff; border-color:#fff; }}
 td.off .dnum {{ color:#c2c8ce; font-size:12px; }}
 td.on {{ color:#fff; cursor:pointer; }}
 td.on:hover {{ filter:brightness(0.94); }}
 td.on.sel {{ outline:3px solid #2f4858; outline-offset:-3px; }}
 td.on .dnum {{ font-size:11px; opacity:.9; display:block; font-weight:600; }}
 td.on .pct {{ display:block; font-size:12px; font-weight:700; }}
 td.on .sym {{ display:block; font-size:9px; line-height:1.1; margin-top:1px; word-break:keep-all; opacity:.95; }}
 .legend {{ font-size:11px; color:#8a939d; margin-top:10px; }}
 .legend span {{ display:inline-block; width:11px; height:11px; border-radius:2px; vertical-align:middle; margin:0 3px 0 10px; }}
 /* 위반 도넛 (월별) */
 .donut-box {{ margin-bottom:16px; }}
 .dtitle {{ font-size:13px; font-weight:600; color:#24292f; margin-bottom:6px; }}
 .donut {{ display:flex; gap:16px; align-items:center; flex-wrap:wrap; }}
 .dcenter {{ font-size:24px; font-weight:700; fill:#24292f; }}
 .dcsub {{ font-size:10px; fill:#8a939d; }}
 .legend2 {{ font-size:12px; }}
 .legend2 .lgi {{ display:flex; align-items:center; gap:7px; margin-bottom:4px; color:#424a53; }}
 .legend2 .sw {{ width:10px; height:10px; border-radius:2px; display:inline-block; }}
 .legend2 b {{ color:#24292f; }}
 .legend2 .lgp {{ color:#8a939d; }}
 .ok {{ color:#3f7d5a; font-size:13px; }}
 /* 핵심 원칙 */
 .cores {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:10px; }}
 .core {{ display:flex; align-items:center; gap:10px; background:#f6f8fa; border:1px solid #d8dee4; border-radius:8px; padding:11px 14px; }}
 .core .cid {{ font-weight:700; color:#2f4858; font-size:12px; background:#e7ecf0; padding:2px 8px; border-radius:5px; white-space:nowrap; }}
 .core .crule {{ font-size:13px; font-weight:500; }}
 /* 일별 피드 */
 .feed {{ display:flex; align-items:center; gap:11px; padding:9px 11px; border:1px solid #e8ebef; border-radius:8px; margin-bottom:6px; cursor:pointer; }}
 .feed:hover {{ background:#f6f8fa; }}
 .feed.sel {{ border-color:#2f4858; background:#f0f3f5; }}
 .feed .fbadge {{ color:#fff; font-size:11px; font-weight:700; padding:3px 8px; border-radius:10px; min-width:40px; text-align:center; }}
 .feed .fmeta {{ display:flex; flex-direction:column; line-height:1.25; }}
 .feed .fdate {{ font-size:12px; font-weight:600; }}
 .feed .fsym {{ font-size:11px; color:#8a939d; }}
 .feed .fnote {{ font-size:12px; color:#424a53; flex:1; }}
 /* 상세 패널 */
 .detailwrap {{ border:1px solid #d8dee4; border-radius:10px; padding:6px 24px 20px; background:#fbfcfd; }}
 .detail h2 {{ font-size:17px; border:0; margin:16px 0 4px; }}
 .detail h3 {{ font-size:14px; margin:18px 0 6px; border-bottom:1px solid #eef1f4; padding-bottom:4px; }}
 .detail h4 {{ font-size:13px; margin:12px 0 4px; color:#57606a; }}
 .detail p {{ font-size:13px; line-height:1.65; }}
 .detail ul {{ font-size:13px; line-height:1.65; padding-left:18px; }}
 .detail blockquote {{ border-left:3px solid #d8dee4; margin:10px 0; padding:6px 14px; color:#57606a; font-size:13px; background:#f6f8fa; border-radius:0 6px 6px 0; }}
 .detail hr {{ border:0; border-top:1px solid #eef1f4; margin:16px 0; }}
 .detail code {{ background:#eef1f4; padding:1px 5px; border-radius:3px; font-size:12px; }}
 table.md {{ border-collapse:collapse; width:100%; font-size:12px; margin:10px 0; }}
 table.md th, table.md td {{ border:1px solid #e8ebef; padding:6px 9px; text-align:left; vertical-align:top; }}
 table.md th {{ background:#f6f8fa; font-weight:600; }}
 /* 기타 원칙 */
 .rcats {{ display:flex; gap:16px; flex-wrap:wrap; }}
 .rcat {{ background:#f6f8fa; border:1px solid #d8dee4; border-radius:8px; padding:6px 16px 10px; flex:1; min-width:220px; }}
 .rcat h3 {{ font-size:13px; color:#2f4858; margin:10px 0 4px; }}
 .rcat ul {{ margin:0; padding-left:16px; }}
 .rcat li {{ font-size:12px; line-height:1.6; color:#424a53; }}
 .rcat li b {{ color:#24292f; }}
 footer {{ color:#c2c8ce; font-size:11px; margin-top:34px; }}
</style></head><body>
 <h1>트레이딩 원칙 준수 대시보드</h1>
 <div class="sub">본인 매매일지 기록 집계 · 기간 {period} · 결과가 아니라 <b>원칙 준수</b>를 추적</div>

 <div class="cards">
   <div class="card"><div class="big">{total_days}</div><div class="lbl">기록일수</div></div>
   <div class="card"><div class="big">{avg_s}</div><div class="lbl">평균 준수율</div></div>
   <div class="card"><div class="big">{streak}</div><div class="lbl">무위반 스트릭(일)</div></div>
   <div class="card"><div class="big">{sum(fail_counter.values())}</div><div class="lbl">누적 위반 수</div></div>
 </div>

 {principles_html}

 <div class="board">
   <div class="col">
     <h2>매매일지 달력 <span class="muted" style="font-weight:400">— 칸을 클릭하면 상세</span></h2>
     <div class="cals">{cals}</div>
     <div class="legend">준수율
       <span style="background:#bd7b73"></span>~39
       <span style="background:#c4a35a"></span>40–59
       <span style="background:#6b9b80"></span>60–79
       <span style="background:#3f7d5a"></span>80+
       <span style="background:#c4c9d0"></span>채점불가
     </div>
     <h2>반복 위반 — 같은 실수 몇 번?</h2>
     {viol_html}
   </div>
   <div class="col">
     <h2>일별 한 줄 요약 <span class="muted" style="font-weight:400">— 클릭하면 상세</span></h2>
     {feed_html}
   </div>
 </div>

 <h2 id="detailtop">상세 분석</h2>
 <div class="detailwrap" id="detailwrap">{detail_html}</div>

 {other_html}

 <footer>generated by trading-coach · build_dashboard.py · 김민우(네프콘 BUY_TRADING_DATA)와 무관한 본인 일지 기록</footer>
 <script>
 function showDay(d) {{
   var ds = document.querySelectorAll('.detail');
   for (var i=0;i<ds.length;i++) ds[i].style.display='none';
   var el = document.getElementById('detail-'+d);
   if (el) el.style.display='block';
   var sel = document.querySelectorAll('[data-date]');
   for (var j=0;j<sel.length;j++) sel[j].classList.toggle('sel', sel[j].getAttribute('data-date')===d);
   var top = document.getElementById('detailtop');
   if (top) top.scrollIntoView({{behavior:'smooth', block:'start'}});
 }}
 window.addEventListener('DOMContentLoaded', function() {{
   var d = "{latest}";
   if (!d) return;
   var sel = document.querySelectorAll('[data-date]');
   for (var j=0;j<sel.length;j++) sel[j].classList.toggle('sel', sel[j].getAttribute('data-date')===d);
 }});
 </script>
</body></html>
"""

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] 대시보드 생성 → {args.out} ({total_days}일 기록, 누적 위반 {sum(fail_counter.values())}건)")


if __name__ == "__main__":
    main()
