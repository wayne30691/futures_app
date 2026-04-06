# 各 Tab 計算公式、指標含意與統計顯著性改善建議

本文件依據目前 `scripts/publish_raw_web.py` 的前端邏輯整理。若後續公式有調整，這份表也應同步更新。

## Tab 一覽

| Tab | 主要內容 | 核心資料來源 |
| --- | --- | --- |
| 策略控制台 | 指定 session、時段、停損停利後，計算波動、勝率、報酬風險與顯著性 | `raw/*.csv` 經 `scripts/publish_raw_web.py` 壓成 1 分 K 後的 `market_1m.json` |
| 波動排名 | 對所有 30 分鐘時段做波動排序與停損停利對照 | 同上 |
| 風險報酬矩陣 | 比較不同時段在多種停損/停利組合下的勝率 | 同上 |
| 財經日曆 | 目前為靜態外部連結區塊，非量化公式驅動 | HTML 靜態內容 |

## 策略控制台

| 項目 | 公式 | 含意 |
| --- | --- | --- |
| Half-hour Slot | 將交易日切成 30 分鐘區間 | 每個時段都是分析單位 |
| `Range` 波動 | `max(high) - min(low)` | 該 30 分鐘內的絕對價格振幅 |
| `ATR Proxy` 波動 | `sqrt(sum((high - low)^2))` | 以每根 bar 高低差平方和近似時段內真實波動強度 |
| `Ret Std` 波動 | `std(r_i) * 10000`，其中 `r_i = (close_i - close_{i-1}) / close_{i-1}` | 以報酬率標準差衡量時段內不穩定度 |
| Avg Volatility | `mean(m_i)` | 近 N 日該時段平均波動 |
| Median Volatility | `percentile(m_i, 50%)` | 抗極端值的中位波動 |
| P75 Volatility | `percentile(m_i, 75%)` | 偏高波動水位參考 |
| Avg Volume | `mean(sum(volume in slot))` | 近 N 日該時段平均成交量 |
| False Breakout Rate | `假突破天數 / N` | 突破時段高低點後，收盤又回到區間內的比率 |
| Expansion Continuation | `波動擴張次數 / (N-1)` | 相鄰日比較下，波動是否持續放大的比例 |
| Volatility Rank | 依所選排序方式對全部時段排名 | 觀察該時段在全時段中的相對位置 |

## 回測與交易模擬

目前 `simulateSlotTrade()` 的規則如下。

| 項目 | 公式 | 含意 |
| --- | --- | --- |
| Entry | `slotBars[0].open` | 30 分鐘時段開始價視為進場價 |
| Direction = long | `dir = +1` | 固定做多 |
| Direction = short | `dir = -1` | 固定做空 |
| Direction = auto | `close_end_of_slot >= open_start ? +1 : -1` | 用該時段自身收盤方向決定多空 |
| Long Stop | `low <= entry - stopPts` | 先碰停損即判負 |
| Long Target | `high >= entry + takePts` | 先碰停利即判勝 |
| Short Stop | `high >= entry + stopPts` | 放空先碰停損即判負 |
| Short Target | `low <= entry - takePts` | 放空先碰停利即判勝 |
| 未觸價出場 | `slot_end_close - entry` 或 `entry - slot_end_close` | 只在該 30 分鐘內評估，不延伸到後續 bars |
| `rs` | `1 / 0 / -1` | 勝 / 平 / 負 |
| `retPct` | `settledPts / entry * 100` | 以進場價標準化的報酬率 |

## 策略控制台統計表

| 指標 | 公式 | 含意 |
| --- | --- | --- |
| Backtest Win Rate | `wins / N * 100%` | 全部樣本中的勝率 |
| Resolved Win Rate | `wins / resolvedN * 100%` | 只看有明確勝負樣本的勝率 |
| Long Win Rate | `longWins / N * 100%` | 固定做多勝率 |
| Short Win Rate | `shortWins / N * 100%` | 固定做空勝率 |
| Backtest Reward/Risk | `mean(+TP/SL, -1)` over resolved trades | 用 R 倍數表示的平均結果 |
| Selected Stop / Target | 使用者輸入值 | 用來控制模擬出場門檻 |

## 波動排名 Tab

| 欄位 | 公式 | 含意 |
| --- | --- | --- |
| Time Slot | `slotLabel(start)` | 30 分鐘時段標籤 |
| Volatility | `mean(metricFromBars(slotBars, mode))` | 該時段近 N 日平均波動 |
| Stop | `sl` | 目前選定停損點數 |
| Target | `tp` | 目前選定停利點數 |
| Target-Stop | `tp - sl` | 可粗略視為可用淨震幅 |
| 排序: 高到低 | `avg desc` | 先看高波動時段 |
| 排序: 低到高 | `avg asc` | 先看低波動時段 |
| 排序: 時間早到晚 | `slotStart asc` | 依時段時間順序檢視全表 |

## 風險報酬矩陣 Tab

| 項目 | 公式 | 含意 |
| --- | --- | --- |
| 勝率矩陣單格 | `wins(slot, sl, tp, dir) / N * 100%` | 某時段在某組 SL/TP 下的命中率 |
| `R/R` | `tp / sl` | 每筆交易理論風報比 |
| 回測排名分數 | 依 direction 選 `avgLong`、`avgShort` 或 `avgAuto` | 排出優先操作時段 |
| Low Risk 標記 | `slotVol <= percentile(slotVols, 40%)` | 波動落在較低 40% 的時段 |
| 切面矩陣是否達標 | `min(多個 lookback 勝率) >= threshold` | 檢查跨 lookback 是否都達到最低門檻 |

## 財經日曆 Tab

| 項目 | 公式 | 含意 |
| --- | --- | --- |
| 財經日曆 | 無 | 目前是輔助資訊區塊，不參與統計計算 |

## 目前統計顯著性區塊

| 指標 | 公式 | 含意 |
| --- | --- | --- |
| 勝率 95% CI | `Wilson CI(x=wins, n=N)` | 比傳統常態近似更適合有限樣本勝率 |
| `H0: 勝率 = 50%` | 以常態近似計算雙尾 p-value | 檢查是否顯著偏離 50% |
| 與其他時段比較 | `twoPropPValue(x1,n1,x2,n2)` | 比較該時段勝率是否顯著高於其他時段 |
| 平均報酬 bootstrap CI | 對 `retPct` 重抽樣後取 2.5% 與 97.5% 分位 | 檢查平均報酬區間是否穩定為正 |
| 樣本外檢驗 | 前 70% train、後 30% test | 用訓練期最佳時段去測試期驗證是否過擬合 |

## 如何提升或改善統計顯著性

| 改善方向 | 建議作法 | 目的 |
| --- | --- | --- |
| 增加樣本數 | 擴大 `TOP_N`、保留更多交易日、按月份分層比較 | 降低估計波動、縮窄信賴區間 |
| 避免多重比較偏誤 | 對多時段、多 SL/TP 組合加入 Bonferroni 或 FDR 校正 | 降低大量搜尋後的假陽性 |
| 提升樣本外驗證強度 | 改成 rolling walk-forward，而非單次 70/30 切分 | 減少單次切分運氣成分 |
| 分 regime 驗證 | 區分高波動日、低波動日、結算日前後、重大事件日 | 檢查策略是否只在特定市場環境有效 |
| 以報酬分佈取代只看勝率 | 增加 expectancy、profit factor、max drawdown、Sharpe-like 指標 | 避免勝率高但賺少賠多 |
| 改善 bootstrap | 使用 block bootstrap 或以交易日為單位重抽樣 | 保留時序相依性，避免低估風險 |
| 改善檢定方法 | 小樣本時用 exact binomial test；報酬分佈偏態時用 permutation test | 讓 p-value 更穩健 |
| 檢查穩定性 | 比較不同 lookback、不同 anchor day 是否一致 | 降低參數敏感度 |
| 納入交易成本 | 加入手續費、滑價、夜盤流動性折減 | 避免統計顯著但實盤無法獲利 |
| 加入效應量 | 除 p-value 外增加勝率差、平均報酬差、Cohen's h 等 | 避免只看顯著、不看實質大小 |

## 建議後續優先補強項目

1. 多重比較校正
2. rolling walk-forward 樣本外驗證
3. 納入手續費與滑價
4. 以交易日 block bootstrap 取代目前單筆重抽樣
5. 增加 expectancy、drawdown、profit factor
