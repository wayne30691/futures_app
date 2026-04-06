"""
從期交所「前30個交易日期貨每筆成交資料」頁面下載最新一筆 CSV（ZIP 內單一 .csv），
存成 raw/{yyyyMMdd-1}夜盤_{yyyyMMdd}早盤.csv：
  - yyyyMMdd-1：第一列「時間」前 10 字元（yyyy/MM/dd）減 1 日
  - yyyyMMdd：同一列「日期」欄（yyyy/MM/dd）
僅保留第 2 欄（商品）經 strip 後為「MTX」；且第 3 欄 strip 後長度須為 6 碼，
並僅保留第 3 欄在所有符合列中之最小值者（表頭仍保留）。
第 4 欄不做數字補 0，僅 strip 並以 str 當成文字寫出。
來源頁：https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

LIST_URL = "https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
CSV_ENCODING = "cp950"
KEEP_CONTRACT = "MTX"
COL3_LEN = 6


def fetch_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=120) as resp:
        return resp.read()


def parse_first_row(html: str) -> tuple[str, str, str]:
    """回傳 (時間儲存格全文, 日期儲存格全文, CSV 之 ZIP 網址)。"""
    tbody_i = html.find("<tbody>")
    if tbody_i < 0:
        raise ValueError("找不到資料表格 tbody")
    tr_i = html.find("<tr", tbody_i)
    tr_end = html.find("</tr>", tr_i)
    if tr_i < 0 or tr_end < 0:
        raise ValueError("找不到表格列")
    first_row = html[tr_i : tr_end + 5]
    tds = re.findall(r'<td align="center">([^<]+)</td>', first_row)
    if len(tds) < 2:
        raise ValueError("無法解析時間或日期欄位")
    time_cell = tds[0].strip()
    date_cell = tds[1].strip()
    urls = re.findall(
        r"window\.open\('(https://www\.taifex\.com\.tw/file/taifex/Dailydownload/DailydownloadCSV/[^']+\.zip)'\)",
        first_row,
    )
    if not urls:
        raise ValueError("找不到 CSV（ZIP）下載網址")
    return time_cell, date_cell, urls[0]


def _yyyymmdd_from_slash_prefix10(s: str, label: str) -> str:
    prefix = s[:10]
    if len(prefix) < 10 or prefix[4] != "/" or prefix[7] != "/":
        raise ValueError(f"{label} 前 10 字元應為 yyyy/MM/dd，實際：{prefix!r}")
    return datetime.strptime(prefix, "%Y/%m/%d").strftime("%Y%m%d")


def col4_as_text(raw: str) -> str:
    """第 4 欄以文字輸出（不補零、不轉數值）。"""
    return str(raw).strip()


def filter_contract_rows_csv_bytes(
    body: bytes, contract: str = KEEP_CONTRACT, col3_len: int = COL3_LEN
) -> tuple[bytes, int, str | None]:
    """
    第 2 欄為 contract；第 3 欄 strip 後長度須為 col3_len，且僅保留第三欄字串最小者。
    第 4 欄依 col4_as_text 轉成文字。
    回傳 (位元組, 保留筆數, 所選第三欄值或無符合時 None)。
    """
    text = body.decode(CSV_ENCODING)
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if header is None:
        return body, 0, None

    col3_min_rows: list[tuple[str, list[str]]] = []
    for row in reader:
        if len(row) <= 2 or row[1].strip() != contract:
            continue
        c3 = row[2].strip()
        if len(c3) != col3_len:
            continue
        col3_min_rows.append((c3, row))

    if not col3_min_rows:
        out_buf = io.StringIO()
        writer = csv.writer(out_buf, lineterminator="\n")
        writer.writerow(header)
        return out_buf.getvalue().encode(CSV_ENCODING), 0, None

    min_c3 = min(c for c, _ in col3_min_rows)
    chosen = [row for c, row in col3_min_rows if c == min_c3]

    out_buf = io.StringIO()
    writer = csv.writer(out_buf, lineterminator="\n")
    writer.writerow(header)
    for row in chosen:
        if len(row) > 3:
            row = list(row)
            row[3] = col4_as_text(row[3])
        writer.writerow(row)
    return out_buf.getvalue().encode(CSV_ENCODING), len(chosen), min_c3


def output_stem(time_cell: str, date_cell: str) -> str:
    """{時間yyyyMMdd-1}夜盤_{日期yyyyMMdd}早盤"""
    prefix_time = time_cell[:10]
    if len(prefix_time) < 10 or prefix_time[4] != "/" or prefix_time[7] != "/":
        raise ValueError(f'"時間"前 10 字元應為 yyyy/MM/dd，實際：{prefix_time!r}')
    d_minus1 = (
        datetime.strptime(prefix_time, "%Y/%m/%d") - timedelta(days=1)
    ).strftime("%Y%m%d")
    d_table = _yyyymmdd_from_slash_prefix10(date_cell, '"日期"')
    return f"{d_minus1}夜盤_{d_table}早盤"


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    raw_dir = project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_bytes(LIST_URL).decode("utf-8", errors="replace")
    time_cell, date_cell, zip_url = parse_first_row(html)
    stem = output_stem(time_cell, date_cell)
    out_path = raw_dir / f"{stem}.csv"

    print(
        f"時間欄: {time_cell!r}，日期欄: {date_cell!r} -> raw 檔名 {stem}.csv"
    )
    print(f"下載: {zip_url}")

    zdata = fetch_bytes(zip_url)
    with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
        csv_members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(csv_members) != 1:
            raise ValueError(f"ZIP 內預期 1 個 .csv，實際：{csv_members}")
        body = zf.read(csv_members[0])

    filtered, n_kept, c3_pick = filter_contract_rows_csv_bytes(body)
    out_path.write_bytes(filtered)
    if c3_pick:
        c3_msg = f"，第3欄最小值 {c3_pick!r}"
    else:
        c3_msg = f"，第3欄無長度{COL3_LEN}之列"
    print(f"已寫入（{KEEP_CONTRACT}）: {out_path}，資料列 {n_kept} 筆{c3_msg}")


if __name__ == "__main__":
    main()
