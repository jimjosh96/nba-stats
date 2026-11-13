# CLAUDE.md

本專案的所有規則寫在 **[AGENTS.md](AGENTS.md)**。開始任何工作前，請先完整閱讀並遵守它。

最重要的五條規則摘要：

1. **數字只能來自 `raw/` 的 CSV**，不可憑記憶填寫；CSV 沒有的球員，先請使用者提供來源。
2. 網頁上的數據表和長條圖一律用 `stat-table`、`bar-chart` 元件，由程式從 CSV 自動產生，不要手打表格。
3. 新增頁面一律複製 `templates/page-template.html`，檔名等於 CSV 的 id，放在 `wiki/players/`、`wiki/teams/` 或 `wiki/topics/`。
4. 每個頁面都要登記在 `data/pages.json`，每次修改都要寫進 `log.md`。
5. 結束前執行 `python tools/check.py`，必須全部通過。
