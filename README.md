# futures_app

台指小型期貨資料抓取、靜態分析頁面產生，以及 GitHub Pages 自動部署專案。

## Repo 結構

```text
futures_app/
├─ .github/workflows/        # GitHub Actions
├─ docs/                     # 專案文件
├─ scripts/                  # 抓資料與建站腳本
├─ raw/                      # 原始 CSV
├─ web/                      # 本機預覽輸出
├─ site/                     # GitHub Pages 部署輸出
├─ src/                      # 其他程式模組
├─ config/ data/ output/     # 其他資料與輸出
└─ README.md
```

## 常用指令

抓最近 30 天原始資料：

```powershell
python scripts/fetch_all_taifex_fut_csv_30d.py
```

抓最新一筆原始資料：

```powershell
python scripts/fetch_latest_taifex_fut_csv.py
```

建立正式輸出：

```powershell
python scripts/publish_raw_web.py
```

建立本機預覽：

```powershell
python scripts/build_preview_web.py
python -m http.server 8080
```

接著開啟 `http://127.0.0.1:8080/web/`

## 文件

- [GitHub Pages 設定](docs/GITHUB_PAGES_SETUP.md)
- [開發流程建議](docs/DEV_WORKFLOW_SUGGESTION.md)
- [各 Tab 公式與顯著性說明](docs/TAB_FORMULAS_AND_SIGNIFICANCE.md)
