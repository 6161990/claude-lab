#!/usr/bin/env python3
"""
구성종목 xlsx 파일을 터미널에 테이블 형식으로 출력합니다.
openpyxl 없이 표준 라이브러리만 사용 (zipfile + xml.etree.ElementTree)
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def load_xlsx(filepath):
    """xlsx 파일을 파싱하여 행 단위 셀 값 리스트로 반환"""
    ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    with zipfile.ZipFile(filepath) as z:
        # 공유 문자열 로드 (s 타입 셀이 참조하는 문자열)
        with z.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
            strings = []
            for si in tree.findall('.//ns:si', ns):
                t_elem = si.find('.//ns:t', ns)
                strings.append(t_elem.text if t_elem is not None else '')

        # 워크시트 데이터 로드
        with z.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            rows = []
            for row in tree.findall('.//ns:row', ns):
                cells = []
                for c in row:
                    t = c.get('t')  # 's' = sharedString, None = 숫자
                    v_elem = c.find('ns:v', ns)

                    if v_elem is not None:
                        v_text = v_elem.text
                        if t == 's':  # 공유 문자열 인덱스
                            cells.append(strings[int(v_text)])
                        else:  # 숫자
                            cells.append(v_text)
                    else:
                        cells.append('')

                rows.append(cells)

    return rows


def format_table(rows, col_widths=None):
    """행 리스트를 정렬된 테이블 문자열로 변환"""
    if not rows:
        return ''

    # 컬럼 너비 자동 결정
    if col_widths is None:
        col_widths = [max(len(str(row[i])) if i < len(row) else 0 for row in rows)
                      for i in range(len(rows[0]))]

    lines = []
    for row_idx, row in enumerate(rows):
        cells = []
        for col_idx, cell in enumerate(row):
            width = col_widths[col_idx] if col_idx < len(col_widths) else 10
            cells.append(str(cell).ljust(width))

        lines.append('  '.join(cells))

        # 헤더 다음 라인 구분
        if row_idx == 0:
            separator = '  '.join('─' * width for width in col_widths)
            lines.append(separator)

    return '\n'.join(lines)


def main():
    # 파일 경로 결정
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # 기본값: 현재 디렉토리에서 구성종목 파일 찾기
        default_file = Path('구성종목(PDF)_2026-06-25.xlsx')
        if default_file.exists():
            filepath = default_file
        else:
            print("❌ 파일을 찾을 수 없습니다.")
            print("   사용법: python3 show_holdings.py [파일경로]")
            sys.exit(1)

    try:
        print(f"\n📊 {filepath} 읽는 중...\n")
        rows = load_xlsx(filepath)

        if not rows:
            print("❌ 파일이 비어 있습니다.")
            return

        # 고정폭 컬럼 너비 설정 (더 읽기 쉬운 출력)
        col_widths = [20, 28, 12, 16, 10]

        # 데이터 타입별로 정렬 준비
        data_rows = rows[1:]  # 헤더 제외
        if data_rows:
            # 비중(%) 컬럼(4번째)으로 내림차순 정렬 (숫자)
            try:
                data_rows.sort(key=lambda x: float(x[4]) if len(x) > 4 else 0, reverse=True)
            except (ValueError, IndexError):
                pass  # 정렬 실패시 원래 순서 유지

        # 테이블 출력
        header_row = [rows[0]]
        all_rows = header_row + data_rows
        table = format_table(all_rows, col_widths)
        print(table)

        # 통계
        print(f"\n📈 총 {len(data_rows)}개 종목")

    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
