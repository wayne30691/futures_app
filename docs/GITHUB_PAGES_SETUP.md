# GitHub Pages 設定說明

這個專案目前已經有 GitHub Actions workflow：

- `.github/workflows/deploy-pages.yml`

它會在每天台北時間 `17:05` 自動執行以下流程：

1. checkout 專案
2. 建立 `raw/` 目錄
3. 執行 `python scripts/fetch_all_taifex_fut_csv_30d.py`
4. 執行 `python scripts/publish_raw_web.py`
5. 將 `site/` 目錄部署到 GitHub Pages

## 目前狀態是否正確

是，這份設定和目前 repo 內的實作一致，重點如下：

- 排程是 `cron: "5 9 * * *"`，也就是 `09:05 UTC = 17:05 Asia/Taipei`
- workflow 產生的是 `site/`，不是 `web/`
- 公開部署不會上傳 `raw/*.csv`
- `scripts/build_preview_web.py` 是本機預覽用途，不在 GitHub Pages workflow 內使用

## GitHub Pages 啟用步驟

1. 將專案推到 GitHub repository
2. 到 `Settings -> Pages`
3. 在 `Build and deployment` 選擇 `Source: GitHub Actions`
4. 確認 `Actions` 頁面可看到 `Build And Deploy MTX Viewer`
5. workflow 第一次成功後，Pages 站點就會可用

## 手動重跑

如果想立即重新部署：

1. 到 GitHub 的 `Actions`
2. 點選 `Build And Deploy MTX Viewer`
3. 點 `Run workflow`

## 注意事項

- 若 TAIFEX 在 `17:05` 時資料仍未完整，當天內容可能偏舊
- 若想更保守，可把 cron 改晚，例如台北時間 `17:20` 或 `17:30`
- `scripts/publish_raw_web.py` 會同時輸出 `web/` 與 `site/`；但 GitHub Pages 只使用 `site/`
