# 修改紀錄

格式說明見 AGENTS.md 第 13 節。新的紀錄放在最上面。

## [2026-11-13] 規則｜避免排名敘述過時
- 新增柯瑞後，發現 6 個球員頁的「6 人中」「本站第 N 名」等敘述已經不正確
- AGENTS.md 第 10 節：新增「不要寫死收錄人數」
- AGENTS.md 第 12 節流程 A：新增第 6 步「重新檢查其他球員頁的排名敘述」
- tools/check.py：新增檢查，頁面出現「N 位球員」「N 人中」會報錯

## [2026-11-13] 更新｜新增柯瑞後修正排名
- shai-gilgeous-alexander：罰球命中率由「本站最高」改為「第 2」
- anthony-edwards：三分與罰球命中率由「第 2」改為「第 3」，摘要同步修改
- jayson-tatum：三分命中率改為「第 6」
- lebron-james：三分命中率改為「第 4」，得分改為「本站最後」
- nikola-jokic、giannis-antetokounmpo：「6 人中」改為「本站球員中」
- anthony-edwards、lebron-james 的 related 加入 stephen-curry

## [2026-11-13] 新增｜stephen-curry
- 新增頁面：wiki/players/stephen-curry.html
- 新增數據：players_2024-25.csv 一列（來源已記錄於 SOURCES.md，MVP 名次查無來源故不記錄）
- 新增 redlink：勇士

## [2026-11-11] 新增｜初版 11 頁
- 新增球員頁：shai-gilgeous-alexander、nikola-jokic、giannis-antetokounmpo、jayson-tatum、lebron-james、anthony-edwards
- 新增球隊頁：oklahoma-city-thunder、cleveland-cavaliers、boston-celtics
- 新增主題分析：mvp-race、point-differential
- 尚未建立（redlink）：金塊、公鹿、湖人、灰狼

## [2026-11-11] 數據｜匯入 2024-25 正規賽數據
- 新增 raw/players_2024-25.csv（6 位球員）與 raw/teams_2024-25.csv（30 隊）
- 來源：Basketball-Reference，詳見 raw/SOURCES.md；已和聯盟排行榜交叉比對

## [2026-11-11] 規則｜建立專案
- 建立 AGENTS.md、CLAUDE.md、頁面範本、樣式、圖表程式與檢查程式
