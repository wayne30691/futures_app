# 開發流程持續改進方向

## 現況

目前 repo 內已存在的正式流程如下：

- 日常部署 workflow：`.github/workflows/deploy-pages.yml`
- 正式發布來源：`main`
- 正式站點內容：`site/`

本機指令分工如下：

```powershell
python scripts/publish_raw_web.py
```

會輸出：

- `web/`
- `site/`

```powershell
python scripts/build_preview_web.py
```

會輸出：

- `web/`

也就是說，`scripts/build_preview_web.py` 適合本機快速預覽；`scripts/publish_raw_web.py` 適合正式產出。

## 這份文件是否正確

大致方向正確，但它屬於「建議中的開發流程」，不是 repo 目前已經完整實作的流程。特別是下面這段要分清楚：

- `main -> GitHub Pages`：這一段目前已實作
- `dev` 或 `preview branch -> preview 站`：這一段目前只是建議，repo 內尚未看到對應 workflow

所以這份文件若保留，建議把它視為 proposal，而不是 current state。

## 建議工作方式

1. 平常開發先在功能分支修改
2. 本機先跑 `python scripts/build_preview_web.py`
3. 用 `python -m http.server 8080` 從 `http://127.0.0.1:8080/web/` 檢查畫面
4. 確認沒問題後再跑 `python scripts/publish_raw_web.py`
5. merge 到 `main` 後，交給 GitHub Actions 自動部署 Pages

## 如果之後要補 preview 環境

可以再新增一條 workflow，讓：

- `main` 發正式站
- `dev` 或 `preview` 分支發預覽站

這樣就能把「本機預覽」和「雲端預覽」分開管理。
