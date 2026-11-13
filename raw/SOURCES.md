# 數據來源

所有數據皆為 **2024-25 球季 NBA 正規賽**，查詢日期 2026-11-11。

| 檔案 | 內容 | 來源 |
|---|---|---|
| players_2024-25.csv | 球員場均數據與獎項 | 各球員的 Basketball-Reference 頁面（Per Game 表格 2024-25 列），例如 https://www.basketball-reference.com/players/g/gilgesh01.html |
| teams_2024-25.csv | 30 隊戰績、場均得失分、SRS | https://www.basketball-reference.com/leagues/NBA_2025_standings.html |

交叉檢查：得分、籃板、助攻與 https://www.basketball-reference.com/leagues/NBA_2025_leaders.html 的聯盟排行榜一致。

## 欄位說明

**players_2024-25.csv**：g 出賽場數、mp 場均上場分鐘、pts 得分、trb 籃板、ast 助攻、stl 抄截、blk 阻攻、tov 失誤、fg_pct 投籃命中率、fg3_pct 三分命中率、ft_pct 罰球命中率（命中率皆為 0～1 的小數）、awards 獎項（MVP-1 代表 MVP 票選第 1 名）。

**teams_2024-25.csv**：w 勝場、l 敗場、pts 場均得分、opp_pts 場均失分、srs 簡單評分系統（綜合淨勝分與賽程強度，越高越強）。

## 新增數據的規則

- 每新增一列，都要在上表或下方列出來源網址。
- 只能從來源複製數字，不可憑記憶填寫。

### 新增紀錄
（目前無）
