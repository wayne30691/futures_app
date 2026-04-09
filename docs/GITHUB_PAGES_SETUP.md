# GitHub Pages 設定說明

這個專案目前已經有 GitHub Actions workflow：

- `.github/workflows/deploy-pages.yml`

它會在以下情況執行：

- push 到 `main`
- 每天台北時間 `16:50`
- 手動點選 `Run workflow`

執行時會進行以下流程：

1. checkout 專案
2. 建立 `raw/` 目錄
3. 執行 `python scripts/fetch_all_taifex_fut_csv_30d.py`
4. 執行 `python scripts/publish_raw_web.py`
5. 將 `site/` 目錄部署到 GitHub Pages

## 目前狀態是否正確

是，這份設定和目前 repo 內的實作一致，重點如下：

- 排程是 `cron: "50 8 * * *"`，也就是 `08:50 UTC = 16:50 Asia/Taipei`
- 平常只要 push 到 `main`，Pages 就會重新建置，不需要等到排程時間
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

## 為什麼 push 後頁面沒更新

常見原因如下：

- Pages 的 `Source` 不是 `GitHub Actions`
- push 的分支不是 `main`
- workflow 執行失敗，所以舊站點仍然保留
- 看的其實是瀏覽器快取，重新整理或無痕視窗可先排除

## 注意事項

- 若 TAIFEX 在 `16:50` 時資料仍未完整，當天內容可能偏舊
- 若想更保守，可把 cron 改晚，例如台北時間 `17:20` 或 `17:30`
- `scripts/publish_raw_web.py` 會同時輸出 `web/` 與 `site/`；但 GitHub Pages 只使用 `site/`
