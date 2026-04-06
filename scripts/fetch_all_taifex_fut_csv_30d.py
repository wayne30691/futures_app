"""
從期交所「前30個交易日期貨每筆成交資料」頁面，將列表上所有可下載日期之 CSV（ZIP）
各下載一次，套用與 fetch_latest_taifex_fut_csv 相同之篩選與檔名規則，寫入 raw/。

檔名：{時間yyyyMMdd-1}夜盤_{日期yyyyMMdd}早盤.csv
處理：僅 MTX、第3欄長度6且取最小契約月、第4欄 strip 後文字輸出（cp950）。

來源頁：https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData
"""

from __future__ import annotations

import io
import re
import sys
import time
import zipfile
from pathlib import Path

from fetch_latest_taifex_fut_csv import (
    COL3_LEN,
    KEEP_CONTRACT,
    LIST_URL,
    fetch_bytes,
    filter_contract_rows_csv_bytes,
    output_stem,
)


CSV_ZIP_RE = re.compile(
    r"window\.open\('(https://www\.taifex\.com\.tw/file/taifex/Dailydownload/DailydownloadCSV/[^']+\.zip)'\)"
)


def parse_all_download_rows(html: str) -> list[tuple[str, str, str]]:
    """自表格 tbody 解析每一列：(時間, 日期, CSV 之 ZIP 網址)。無下載連結則略過。"""
    tbody_start = html.find("<tbody>")
    if tbody_start < 0:
        raise ValueError("找不到資料表格 tbody")
    tbody_end = html.find("</tbody>", tbody_start)
    if tbody_end < 0:
        tbody_end = len(html)
    chunk = html[tbody_start:tbody_end]

    rows: list[tuple[str, str, str]] = []
    pos = 0
    while True:
        tr_s = chunk.find("<tr", pos)
        if tr_s < 0:
            break
        tr_e = chunk.find("</tr>", tr_s)
        if tr_e < 0:
            break
        tr_html = chunk[tr_s : tr_e + 5]
        pos = tr_e + 5

        tds = re.findall(r'<td align="center">([^<]+)</td>', tr_html)
        if len(tds) < 2:
            continue
        time_cell = tds[0].strip()
        date_cell = tds[1].strip()
        m = CSV_ZIP_RE.search(tr_html)
        if not m:
            continue
        rows.append((time_cell, date_cell, m.group(1)))
    return rows


def csv_bytes_from_zip(zdata: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"ZIP 內預期 1 個 .csv，實際：{names}")
        return zf.read(names[0])


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    raw_dir = project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(f"抓取列表: {LIST_URL}")
    html = fetch_bytes(LIST_URL).decode("utf-8", errors="replace")
    table_rows = parse_all_download_rows(html)
    if not table_rows:
        print("未解析到任何可下載列。", file=sys.stderr)
        sys.exit(1)

    print(f"共 {len(table_rows)} 個下載項目，寫入 {raw_dir}")
    delay_s = 0.35
    ok = 0
    for i, (time_cell, date_cell, zip_url) in enumerate(table_rows, start=1):
        try:
            stem = output_stem(time_cell, date_cell)
        except ValueError as e:
            print(f"[{i}/{len(table_rows)}] 略過（檔名解析失敗）{time_cell!r} / {date_cell!r}: {e}")
            continue
        out_path = raw_dir / f"{stem}.csv"
        print(f"[{i}/{len(table_rows)}] {stem}.csv  <- {zip_url}")
        try:
            zdata = fetch_bytes(zip_url)
            body = csv_bytes_from_zip(zdata)
            filtered, n_kept, c3_pick = filter_contract_rows_csv_bytes(body)
            out_path.write_bytes(filtered)
            c3_msg = f"第3欄 {c3_pick!r}" if c3_pick else f"無長度{COL3_LEN}第3欄"
            print(f"    完成 資料列 {n_kept} 筆（{KEEP_CONTRACT}，{c3_msg}）")
            ok += 1
        except OSError as e:
            print(f"    寫入失敗 {out_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"    失敗: {e}", file=sys.stderr)
        if i < len(table_rows):
            time.sleep(delay_s)

    print(f"結束：成功 {ok} / {len(table_rows)}")


if __name__ == "__main__":
    main()
