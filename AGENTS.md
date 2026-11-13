# AGENTS.md：NBA 數據小站

> 給 AI 的專案說明書。開始任何修改前，請**完整讀完這份文件**，並照著做。
> 如果這份文件和使用者的要求衝突，先照使用者的要求做，並在回覆中說明哪一條規則被改變了。

---

## 1. 專案目的

「NBA 數據小站」用數據介紹 NBA 的球員和球隊，並做一些簡單的主題分析。目前收錄 **2024-25 球季正規賽**。

核心設計是：**數字只存在 CSV 裡，網頁上的數據表和圖表都由程式自動從 CSV 產生。**

```
raw/*.csv（數據）  ──┐
                    ├→ assets/main.js 自動產生數據表、長條圖
wiki/*.html（文字）──┘
data/pages.json（頁面目錄）→ 首頁卡片與搜尋
```

這樣設計的好處：
- 新增一位球員時，只要在 CSV 加一列，**所有比較圖都會自動更新**。
- 網頁上不會出現手打錯的數字。
- AI 只需要寫「文字解讀」，不用排版表格或畫圖。

---

## 2. 技術規範

- 只用 **HTML + CSS + 原生 JavaScript**，不要使用框架、建置工具或外部圖表函式庫。
- 所有連結一律用**相對路徑**（例如 `../../assets/style.css`），不要用 `/` 開頭。
- 樣式只寫在 `assets/style.css`，不要寫 `style="..."` 或 `<style>`。
- 共用程式只寫在 `assets/main.js`。

---

## 3. 資料夾結構

```
nba-stats/
├── AGENTS.md                ← 本文件：給 AI 的規則
├── CLAUDE.md                ← 給 Claude Code 的入口，指向本文件
├── README.md                ← 給人看的專案介紹
├── index.html               ← 首頁
├── log.md                   ← 修改紀錄
├── assets/
│   ├── style.css            ← 唯一的樣式檔
│   └── main.js              ← 讀 CSV、畫數據表與長條圖、首頁卡片
├── data/
│   └── pages.json           ← 所有頁面的目錄
├── raw/
│   ├── players_2024-25.csv  ← 球員數據
│   ├── teams_2024-25.csv    ← 球隊數據（30 隊）
│   └── SOURCES.md           ← 數據來源與欄位說明
├── templates/
│   └── page-template.html   ← 新增頁面時複製這個檔案
├── tools/
│   └── check.py             ← 規則檢查程式
└── wiki/
    ├── players/             ← 球員頁
    ├── teams/               ← 球隊頁
    └── topics/              ← 主題分析頁
```

---

## 4. 數據規則（最重要）

1. **數字只能來自 `raw/` 的 CSV。** 絕對不可以憑記憶填寫任何數據。
2. **網頁上不要手打數據表格。** 數據表和長條圖一律用第 6 節的元件，由程式從 CSV 產生。
3. 文字中可以引用數字，但必須和 CSV **完全相同**，並註明是「2024-25 正規賽」。
4. CSV 只能**新增列**，不能修改既有的數字。來源更正數據時例外，必須在 `log.md` 寫明原因。
5. 新增一列數據時，必須在 `raw/SOURCES.md` 的「新增紀錄」寫下來源網址。
6. 使用者要求新增的球員或球隊**不在 CSV 裡**時，先停下來，請使用者提供 Basketball-Reference 網址或數據，不可以自己編。
7. 命中率在 CSV 裡是 0～1 的小數（例如 `0.519`），顯示時由程式轉成百分比。

### CSV 欄位（不可改名、不可調換順序）

`players_2024-25.csv`：
`id,name,name_zh,team,pos,age,g,mp,pts,trb,ast,stl,blk,tov,fg_pct,fg3_pct,ft_pct,awards`

`teams_2024-25.csv`：
`id,name,name_zh,abbr,conf,w,l,pts,opp_pts,srs`

各欄位的意思寫在 `raw/SOURCES.md`。

---

## 5. 頁面分類與必備區塊

| 分類 id | 中文 | 資料夾 | 必備區塊（`<section>` 的 id，依序排列） |
|---|---|---|---|
| `players` | 球員 | `wiki/players/` | `overview` 球員概況 → `stats` 本季數據 → `analysis` 數據解讀 |
| `teams` | 球隊 | `wiki/teams/` | `overview` 球隊概況 → `stats` 本季數據 → `analysis` 數據解讀 |
| `topics` | 主題分析 | `wiki/topics/` | `question` 分析問題 → `chart` 圖表 → `findings` 發現 → `method` 計算方式 |

所有頁面**最後**都要有這兩個區塊，順序固定：
1. `related` 相關頁面（由程式依 pages.json 自動產生，HTML 只放空容器）
2. `sources` 資料來源（列出用到的 CSV 檔）

每個區塊的寫法：

- **球員、球隊的 `stats` 區塊**：必須包含一個數據表元件，並至少一張長條圖（見第 6 節）。
- **`analysis` 數據解讀**：寫 2～4 個重點，每點先講結論，再用數字支持，例如「得分是聯盟第一：場均 32.7 分」。
- **主題分析的 `chart` 區塊**：至少一張長條圖。
- **`method` 計算方式**：說明用了哪些欄位、怎麼算，例如「淨勝分 = pts − opp_pts」。

每個頁面標題下都要有：
- 一句話摘要 `<p class="summary">`：40 字以內，和 pages.json 的 `summary` 相同。
- 資訊卡 `<aside class="infobox">`：用 `<dl>` 列出 3～5 項基本資料（球隊、位置、所屬分區等文字資料）。

---

## 6. 數據元件（自動從 CSV 產生）

### 數據表

```html
<div class="stat-table" data-source="players" data-id="nikola-jokic"></div>
```

- `data-source`：`players` 或 `teams`
- `data-id`：CSV 的 id，球員頁和球隊頁必須等於**本頁的 id**

### 長條圖

```html
<figure class="bar-chart" data-source="players" data-metric="pts"
        data-highlight="nikola-jokic" data-limit="10"></figure>
```

| 屬性 | 必填 | 說明 |
|---|---|---|
| `data-source` | 是 | `players` 或 `teams` |
| `data-metric` | 是 | 要比較的指標，只能用下表的值 |
| `data-highlight` | 否 | 要用橘色標示的 id，多個用逗號分隔 |
| `data-limit` | 否 | 只顯示前幾名 |
| `data-conf` | 否 | 只顯示某分區的球隊：`東區` 或 `西區` |
| `data-order` | 否 | `desc`（預設，大到小）或 `asc`（小到大，適合失分、失誤） |

可用的指標（定義在 `assets/main.js` 的 `METRICS`）：

| 來源 | 指標 |
|---|---|
| `players` | `pts` 得分、`trb` 籃板、`ast` 助攻、`stl` 抄截、`blk` 阻攻、`tov` 失誤、`mp` 上場時間、`g` 出賽、`fg_pct` 投籃命中率、`fg3_pct` 三分命中率、`ft_pct` 罰球命中率 |
| `teams` | `w` 勝場、`win_pct` 勝率、`pts` 場均得分、`opp_pts` 場均失分、`net` 淨勝分、`srs` SRS |

`win_pct` 和 `net` 是程式算出來的，不在 CSV 裡。需要新的計算指標時，先加到 `main.js` 的 `METRICS`、`tools/check.py` 的 `METRICS`，並更新本表。

---

## 7. 檔案命名規則

- 檔名使用**英文小寫 + 連字號**，**等於 CSV 裡的 id**：
  - 球員：英文全名，例如 `nikola-jokic.html`（去掉重音符號）
  - 球隊：英文全名，例如 `oklahoma-city-thunder.html`
  - 主題分析：描述主題的英文，例如 `mvp-race.html`
- 檔名（不含 .html）就是頁面 id，pages.json 的 `id` 必須相同。

---

## 8. pages.json 欄位規範

```json
{
  "id": "nikola-jokic",
  "title": "約基奇 Nikola Jokić",
  "category": "players",
  "path": "wiki/players/nikola-jokic.html",
  "summary": "場均大三元的中鋒，籃板、助攻、抄截都是本站第一。",
  "tags": ["DEN", "中鋒", "MVP-2"],
  "related": ["shai-gilgeous-alexander", "denver-nuggets"],
  "sources": ["players_2024-25.csv"],
  "updated": "2026-11-11"
}
```

| 欄位 | 規則 |
|---|---|
| `title` | 球員：`中文名 英文名`；球隊：`中文隊名 英文隊名`；主題：中文標題 |
| `category` | `players`、`teams`、`topics` 之一 |
| `path` | `wiki/<分類>/<id>.html` |
| `summary` | 40 字以內，和頁面上的摘要相同 |
| `tags` | 2～5 個 |
| `related` | 2～5 個**已存在**的頁面 id，不可包含自己 |
| `sources` | `raw/` 裡實際存在的 CSV 檔名 |
| `updated` | `YYYY-MM-DD` |

---

## 9. HTML 頁面寫法

- 一律**複製 `templates/page-template.html`** 再修改。
- `<body>` 要有 `data-page-id`（頁面 id）和 `data-root`（wiki 頁固定是 `../../`）。
- `<title>` 格式：`頁面標題｜NBA 數據小站`
- 提到**已有頁面**的球員、球隊或主題時，第一次出現加上連結：
  `<a class="wikilink" href="../teams/denver-nuggets.html">金塊</a>`
- 提到**還沒有頁面**的，用 `<span class="redlink" title="尚未建立頁面">湖人</span>` 標示。

---

## 10. 寫作風格

- 使用**台灣習慣的繁體中文**與台灣常用譯名（例如：塞爾提克、金塊、亞歷山大、約基奇）。
- 語氣像運動數據專欄：**先講結論，再給數字**，句子短。
- 比較時要說清楚和誰比，例如「在本站收錄球員中最高」，不要只說「很高」。
- **不要在文字中寫死收錄人數**（例如「6 位球員」「6 人中」），一律寫「本站收錄球員中」，否則新增球員後文字就會過時。
- **只寫數據看得出來的事。** 不寫「史上最強」「被低估」這類數據無法證明的評價，也不寫 CSV 以外的比賽、傷病或交易消息。
- 不使用表情符號。

---

## 11. 視覺風格

主題是「夜間球場的數據看板」：深藍底色、籃球橘強調、數字用等寬字體。

| 用途 | CSS 變數 | 顏色 |
|---|---|---|
| 主色（頁首、標題） | `--court` | `#13213c` |
| 強調色（高亮長條、連結） | `--orange` | `#f26b1d` |
| 一般長條 | `--bar` | `#9fb3d1` |
| 背景 | `--bg` | `#f4f6fa` |
| 卡片 | `--card` | `#ffffff` |

分類標籤顏色：球員 `--cat-players`、球隊 `--cat-teams`、主題分析 `--cat-topics`。

可用的 class：`summary`、`infobox`、`section`、`wikilink`、`redlink`、`badge`、`tag`、`stat-table`、`bar-chart`、`callout`。需要新樣式時，先加到 `style.css` 並更新本節。

**不要**使用 NBA 或球隊的官方 Logo、球員照片。

---

## 12. 常見工作流程

### A. 新增球員頁（例如「新增 Stephen Curry」）

1. 檢查 `raw/players_2024-25.csv` 有沒有這位球員。
   - **沒有**：請使用者提供 Basketball-Reference 網址或數據，依來源新增一列，並在 `raw/SOURCES.md` 記錄來源。
2. 複製範本到 `wiki/players/<id>.html`，id 和 CSV 相同。
3. 填寫 `overview`、`stats`（數據表 + 長條圖）、`analysis`。
4. 在 `data/pages.json` 新增一筆。
5. 把其他頁面中這位球員的 `redlink` 改成 `wikilink`。
6. **重新檢查其他球員頁的排名敘述。** 新球員加入後，「本站第 N 名」「本站最高」這類說法可能改變，逐一和 CSV 比對並更新，被修改的頁面也要更新 `updated`。
7. 在 `log.md` 記錄，執行 `python tools/check.py`。

### B. 新增主題分析（例如「分析哪些球隊防守最好」）

1. 確認需要的欄位在 CSV 裡；需要新的計算指標，照第 6 節的規則新增。
2. 複製範本到 `wiki/topics/<id>.html`，寫 `question` → `chart` → `findings` → `method`。
3. 登記 pages.json、寫 log、執行檢查程式。

### C. 更新到新球季

1. 新增 `raw/players_2025-26.csv` 等新檔案，**不要覆蓋舊球季**。
2. 先修改本文件的數據規則與 `main.js` 讀取的檔名，在 `log.md` 用「規則」類型記錄。

### D. 健康檢查（Lint）

1. 執行 `python tools/check.py`。
2. 人工檢查：文字中的數字是否都和 CSV 一致、有沒有數據無法支持的評價、哪些 `redlink` 已經有數據可以建立頁面。

---

## 13. log.md 格式

每次修改在檔案**最上方**新增一筆：

```
## [2026-11-18] 新增｜stephen-curry
- 新增頁面：wiki/players/stephen-curry.html
- 新增數據：players_2024-25.csv 一列（來源已記錄於 SOURCES.md）
- 更新頁面：golden-state-warriors（redlink 改為 wikilink）
```

類型只能是：`新增`、`更新`、`數據`、`Lint`、`規則`。

---

## 14. 禁止事項

- 憑記憶填寫或修改任何數字。
- 在 HTML 手打數據表格（請用 `stat-table` 元件）。
- 使用外部圖表函式庫、框架或建置工具。
- 寫 inline style 或新增 CSS 檔。
- 使用官方 Logo 或球員照片。
- 新增頁面卻沒有更新 pages.json 和 log.md。

---

## 15. 完成前檢查清單

- [ ] `python tools/check.py` 全部通過
- [ ] 新頁面從範本複製而來，必備區塊齊全且順序正確
- [ ] 球員、球隊頁的 `stat-table` 的 `data-id` 等於頁面 id
- [ ] 文字中的每個數字都能在 CSV 找到
- [ ] 新增球員後，其他頁面的「本站第 N 名」敘述都已重新確認
- [ ] 新增的數據已在 SOURCES.md 記錄來源
- [ ] 其他頁面的 `redlink` 已更新
- [ ] `log.md` 已新增紀錄
