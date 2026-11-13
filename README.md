# NBA 數據小站

用數據看 2024-25 NBA 正規賽的球員與球隊。由 AI 依照 `AGENTS.md` 的規則維護，網頁上的數據表和長條圖都由程式從 CSV 自動產生。

- 網站：https://jimjosh96.github.io/nba-stats/
- 規則：[AGENTS.md](AGENTS.md)（給 AI 看的專案說明書）
- 數據來源：Basketball-Reference，詳見 [raw/SOURCES.md](raw/SOURCES.md)

## 運作方式

```
raw/*.csv（數據）→ assets/main.js 自動產生數據表與長條圖
wiki/*.html（AI 撰寫的文字解讀）
data/pages.json（頁面目錄）→ 首頁卡片與搜尋
```

## 如何新增內容

對 AI（Claude Code、Codex 等）說：

- 「新增 Stephen Curry 的球員頁」（AI 會先確認 CSV 有沒有他的數據，沒有就請你提供來源）
- 「新增金塊的球隊頁」
- 「做一個主題分析：哪些球隊防守最好」
- 「做一次 Lint 健康檢查」

最後執行：

```bash
python tools/check.py
```

## 本機預覽

網頁需要讀取 CSV 和 JSON，請用本機伺服器開啟：

```bash
python -m http.server 8000
# 瀏覽 http://localhost:8000
```

## 聲明

本網站為課堂作業，非 NBA 官方網站，未使用任何官方 Logo 或球員照片。
