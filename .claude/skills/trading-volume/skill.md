---
name: trading-volume
description: "네이버 프리미엄콘텐츠(네프콘) 매매일지 URL을 받아 로그인→차트 이미지 수집→B/S 마커 판독→키움 분봉 API로 매수 시점 누적 거래대금을 계산해 종목별 리포트(BUY_TRADING_DATA.md)를 만든다. '매매일지 분석', '거래대금 정리', '네프콘 매매 분석', '매수 시점 거래대금', '트레이더 분석' 요청 시 사용. 이미 정리된 날짜 이후의 신규 날짜만 증분 처리한다."
---

# 매매일지 거래대금 분석 (Trading Volume)

네프콘 매매일지 글(URL)을 받아 **매수/매도 시점의 누적 거래대금**을 종목별로 정리하는 워크플로.
결과는 `BUY_TRADING_DATA.md`(사진 + ①매수 직전 5분 가속표 + ②일중 추이 B/S 표시)로 누적 관리한다.

## 사전 조건 (필수)

1. **네프콘 세션**: 프로젝트 루트의 `blog/nepcon-mcp/nepcon_browser.py` + `.nepcon_session.json` 사용(로그인 자동).
   - 환경변수 `NEPCON_ID`, `NEPCON_PW` 필요할 수 있음(세션 만료 시 재로그인).
2. **키움 REST API 키**(분봉 조회):
   ```bash
   export KIWOOM_APPKEY="..."   export KIWOOM_SECRETKEY="..."   export KIWOOM_ENV="real"
   ```
   - 키움 분봉(ka10080)은 약 1년치 보유 → 최근 날짜만 조회 가능.
3. Python 패키지: `requests`, `playwright`(네프콘), `pillow`(크롭).

## 증분 원칙

- `report_data.json`(누적 저장소)에 이미 처리한 `(일자,종목코드)`가 기록됨.
- **이미 있는 날짜는 건너뛰고, 신규 날짜만** 추가 → `BUY_TRADING_DATA.md` 전체를 일자순으로 재생성.

---

## 워크플로 (5단계)

### STEP 1. 이미지 수집
```bash
python3 .claude/skills/trading-volume/scripts/download_images.py --urls <URL1> <URL2> ... --out charts/
```
- 각 URL의 매매일지 이미지를 `charts/`에 저장(`chart_<날짜>_<n>.png`), `image_manifest.json` 기록.

### STEP 2. 차트 판독 (★ Claude 비전 작업 — 스크립트화 불가)
각 종목 대표 차트에서 다음을 읽어 `targets.json`을 만든다.

**판독 방법**:
- 상단 정보바 크롭(`crop(110,156,760,206)` ×3배) → **종목코드·종목명** 확인.
- 가격영역 크롭(`crop(110,180,1185,335)` ×1.8배) → **최고/최저 앵커(시각 표시)**, **B(빨강 원/박스)=매수·S(파랑 방패/박스)=매도** 마커의 가격·위치 파악.
- 마커 가격을 분봉과 매칭해 시각 특정(겹치면 군집 구간으로). 시초 급등은 09:00~09:30에 몰림.

**targets.json 스키마**:
```json
[
  {"date":"2026-06-02","name":"종목명","code":"000000",
   "img":"charts/chart_xxx.png","buy_time":"1030",
   "markers":[["B","1030"],["B","1033"],["S","1036"]]}
]
```
- `buy_time`: 대표(1차) 매수 시각 HHMM. `markers`: (B/S, HHMM) 목록.

### STEP 3. 분봉 수집
```bash
python3 .claude/skills/trading-volume/scripts/fetch_minute.py --targets targets.json --out minute_raw/
```
- 각 `(date,code)`의 1분봉을 `minute_raw/<date>_<code>.json`에 저장(키움 ka10080, 연속조회).

### STEP 4. 리포트 생성(증분)
```bash
python3 .claude/skills/trading-volume/scripts/build_report.py --targets targets.json \
    --raw minute_raw/ --store report_data.json --out BUY_TRADING_DATA.md
```
- 분봉에서 자동 계산: 일중 누적 추이(09:30~15:20), 매수 직전 -5~-1분 가속, 매수 직전 5분 vs 매수 후 5분, **선취매/추격매 판단**, B/S 시점 매핑.
- `report_data.json`에 병합 후 `BUY_TRADING_DATA.md` 전체 재생성(일자순).

### STEP 5. 검수
- 이미지 참조 누락 0 확인, `acc_trde_qty`(API 누적거래량)와 합산 일치로 데이터 완전성 검증.

---

## 핵심 정의 (리포트에 명시)

- **누적 거래대금** = 해당일 **09:00 개장부터** 분당(거래량×대표가(고+저+종)/3) 합산. (분봉에 거래대금 필드 없어 환산)
- **현재가/거래대금**은 그날 캡처 시점 값(오늘 아님).
- **매수 직전 5분간 증가** = cum(매수) − cum(매수−5분).
- **매수 후 5분간 증가** = cum(매수+5분) − cum(매수).
- **선취매**(매수 후 더 터짐) vs **추격매**(매수 전 이미 터짐).
- 정확도: 누적 거래량=API 정확값 / 거래대금=±1~2% 추정 / 매매 시각=마커 판독 ±2~3분.

## 한계
- 김씨 실제 체결내역은 본인 계좌 API라야 정확 → 마커는 차트 판독값.
- 급등에 마커가 겹치면 분 단위 분리 불가 → 군집 구간으로 표기.
- 키움 분봉 보유기간(~1년) 밖 날짜는 조회 불가.
