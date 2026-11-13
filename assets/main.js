// NBA 數據小站 — 共用程式（規則見 AGENTS.md 第 6 節）
// 1. 讀取 raw/ 的 CSV，產生數據表（.stat-table）與長條圖（.bar-chart）
// 2. 首頁：讀取 data/pages.json，產生卡片、搜尋與篩選
// 3. 各頁：依 pages.json 的 related 產生「相關頁面」

const CATEGORIES = { players: "球員", teams: "球隊", topics: "主題分析" };

const DATA_FILES = {
  players: "raw/players_2024-25.csv",
  teams: "raw/teams_2024-25.csv",
};

// 可用的指標。type：num 一般數字、pct 命中率（0～1 顯示成 %）、int 整數
// calc：由其他欄位算出來的指標
const METRICS = {
  players: {
    pts: { label: "得分", type: "num" },
    trb: { label: "籃板", type: "num" },
    ast: { label: "助攻", type: "num" },
    stl: { label: "抄截", type: "num" },
    blk: { label: "阻攻", type: "num" },
    tov: { label: "失誤", type: "num" },
    mp: { label: "上場分鐘", type: "num" },
    g: { label: "出賽", type: "int" },
    fg_pct: { label: "投籃命中率", type: "pct" },
    fg3_pct: { label: "三分命中率", type: "pct" },
    ft_pct: { label: "罰球命中率", type: "pct" },
  },
  teams: {
    w: { label: "勝場", type: "int" },
    win_pct: { label: "勝率", type: "pct", calc: (t) => t.w / (t.w + t.l) },
    pts: { label: "場均得分", type: "num" },
    opp_pts: { label: "場均失分", type: "num" },
    net: { label: "淨勝分", type: "signed", calc: (t) => t.pts - t.opp_pts },
    srs: { label: "SRS", type: "signed" },
  },
};

// 數據表要顯示的指標
const TABLE_METRICS = {
  players: ["pts", "trb", "ast", "stl", "blk", "tov", "fg_pct", "fg3_pct", "ft_pct", "mp", "g"],
  teams: ["w", "win_pct", "pts", "opp_pts", "net", "srs"],
};

const LOWER_IS_BETTER = new Set(["tov", "opp_pts"]);
const root = document.body.dataset.root || "";
const SEASON_NOTE = "2024-25 正規賽";

// ---------- 工具 ----------
function escapeHTML(text) {
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}

function parseCSV(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.filter(Boolean).map((line) => {
    const cells = line.split(",");
    const row = {};
    headers.forEach((h, i) => {
      const value = cells[i] ?? "";
      row[h] = value !== "" && !isNaN(value) ? Number(value) : value;
    });
    return row;
  });
}

function metricValue(source, row, key) {
  const m = METRICS[source][key];
  return m.calc ? m.calc(row) : row[key];
}

function formatValue(source, key, value) {
  const type = METRICS[source][key].type;
  if (type === "pct") return (value * 100).toFixed(1) + "%";
  if (type === "int") return String(Math.round(value));
  if (type === "signed") return (value > 0 ? "+" : "") + value.toFixed(1);
  return value.toFixed(1);
}

function displayName(source, row) {
  return source === "players" ? row.name_zh : row.name_zh;
}

async function loadData() {
  const entries = await Promise.all(
    Object.entries(DATA_FILES).map(async ([key, file]) => {
      const res = await fetch(root + file);
      if (!res.ok) throw new Error(`無法讀取 ${file}`);
      return [key, parseCSV(await res.text())];
    })
  );
  return Object.fromEntries(entries);
}

async function loadPages() {
  const res = await fetch(`${root}data/pages.json`);
  if (!res.ok) throw new Error("無法讀取 pages.json");
  return res.json();
}

// ---------- 數據表 ----------
function rankOf(source, rows, row, key) {
  const lowerBetter = LOWER_IS_BETTER.has(key);
  const sorted = [...rows].sort((a, b) => {
    const diff = metricValue(source, b, key) - metricValue(source, a, key);
    return lowerBetter ? -diff : diff;
  });
  return sorted.findIndex((r) => r.id === row.id) + 1;
}

function renderStatTable(el, data) {
  const source = el.dataset.source;
  const rows = data[source];
  const row = rows.find((r) => r.id === el.dataset.id);
  if (!row) {
    el.innerHTML = `<p class="empty">CSV 中找不到 ${escapeHTML(el.dataset.id)}。</p>`;
    return;
  }
  const scope = source === "players" ? "本站球員" : "聯盟";
  el.innerHTML = TABLE_METRICS[source]
    .map((key) => {
      const value = metricValue(source, row, key);
      const rank = rankOf(source, rows, row, key);
      return `<div class="stat-cell">
          <b>${formatValue(source, key, value)}</b>
          <span>${METRICS[source][key].label}</span>
          <span class="rank">${scope}第 ${rank} ${LOWER_IS_BETTER.has(key) ? "少" : "高"}</span>
        </div>`;
    })
    .join("");
  el.setAttribute("aria-label", `${displayName(source, row)} ${SEASON_NOTE}數據`);
}

// ---------- 長條圖 ----------
function renderBarChart(el, data) {
  const { source, metric } = el.dataset;
  const info = METRICS[source]?.[metric];
  if (!info) {
    el.innerHTML = `<p class="empty">不支援的指標：${escapeHTML(metric)}</p>`;
    return;
  }
  const highlight = new Set((el.dataset.highlight || "").split(",").map((s) => s.trim()).filter(Boolean));
  const order = el.dataset.order === "asc" ? 1 : -1;
  let rows = data[source].filter((r) => !el.dataset.conf || r.conf === el.dataset.conf);
  rows = rows
    .map((r) => ({ row: r, value: metricValue(source, r, metric) }))
    .sort((a, b) => order * (a.value - b.value));
  if (el.dataset.limit) rows = rows.slice(0, Number(el.dataset.limit));

  const values = rows.map((r) => r.value);
  const min = Math.min(0, ...values);
  const max = Math.max(0, ...values);
  const span = max - min || 1;
  const zero = ((0 - min) / span) * 100;

  const scope = [
    source === "players" ? "本站收錄球員" : el.dataset.conf ? `${el.dataset.conf}球隊` : "30 隊",
    el.dataset.limit ? `前 ${el.dataset.limit} 名` : "",
  ].filter(Boolean).join("・");

  const bars = rows
    .map(({ row, value }) => {
      const left = value >= 0 ? zero : ((value - min) / span) * 100;
      const width = (Math.abs(value) / span) * 100;
      const cls = ["bar-row", highlight.has(row.id) ? "is-highlight" : ""].join(" ");
      return `<div class="${cls}">
          <span class="bar-label" title="${escapeHTML(row.name)}">${escapeHTML(displayName(source, row))}</span>
          <span class="bar-track">
            <span class="bar-fill${value < 0 ? " negative" : ""}" style="left:${left}%;width:${width}%"></span>
            ${min < 0 ? `<span class="bar-zero" style="left:${zero}%"></span>` : ""}
          </span>
          <span class="bar-value">${formatValue(source, metric, value)}</span>
        </div>`;
    })
    .join("");
  el.innerHTML = `<figcaption>${info.label}<small>${scope}｜${SEASON_NOTE}</small></figcaption>${bars}`;
}

// ---------- 卡片 ----------
function cardHTML(page) {
  const tags = (page.tags || []).map((t) => `<span class="tag">${escapeHTML(t)}</span>`).join("");
  return `<a class="card cat-${page.category}" href="${root}${page.path}">
      <span class="badge cat-${page.category}">${CATEGORIES[page.category] || page.category}</span>
      <h3>${escapeHTML(page.title)}</h3>
      <p>${escapeHTML(page.summary)}</p>
      <div>${tags}</div>
    </a>`;
}

function renderHome(pages, data) {
  const container = document.querySelector("[data-catalog]");
  const search = document.querySelector("[data-search]");
  const filters = document.querySelectorAll("[data-filter]");
  let active = "all";

  document.querySelector("[data-stat-pages]").textContent = pages.length;
  document.querySelector("[data-stat-players]").textContent = data.players.length;
  document.querySelector("[data-stat-teams]").textContent = data.teams.length;

  function draw() {
    const keyword = search.value.trim().toLowerCase();
    container.innerHTML = Object.entries(CATEGORIES)
      .filter(([id]) => active === "all" || active === id)
      .map(([id, name]) => {
        const list = pages.filter(
          (p) => p.category === id &&
            [p.title, p.summary, ...(p.tags || [])].join(" ").toLowerCase().includes(keyword)
        );
        const body = list.length
          ? `<div class="card-grid">${list.map(cardHTML).join("")}</div>`
          : `<p class="empty">沒有符合的頁面。</p>`;
        return `<section class="category-block" id="${id}"><h2>${name}<small>${list.length} 頁</small></h2>${body}</section>`;
      })
      .join("");
  }
  search.addEventListener("input", draw);
  filters.forEach((btn) =>
    btn.addEventListener("click", () => {
      active = btn.dataset.filter;
      filters.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      draw();
    })
  );
  draw();
  if (location.hash) document.querySelector(location.hash)?.scrollIntoView();
}

function renderRelated(pages) {
  const box = document.querySelector("[data-related]");
  if (!box) return;
  const current = pages.find((p) => p.id === document.body.dataset.pageId);
  const related = (current?.related || []).map((id) => pages.find((p) => p.id === id)).filter(Boolean);
  box.innerHTML = related.length ? related.map(cardHTML).join("") : `<p class="empty">尚無相關頁面。</p>`;
}

// ---------- 啟動 ----------
Promise.all([loadPages(), loadData()])
  .then(([pages, data]) => {
    document.querySelectorAll(".stat-table").forEach((el) => renderStatTable(el, data));
    document.querySelectorAll(".bar-chart").forEach((el) => renderBarChart(el, data));
    if (document.querySelector("[data-catalog]")) renderHome(pages, data);
    renderRelated(pages);
  })
  .catch((error) => {
    document.querySelectorAll(".stat-table, .bar-chart, [data-catalog], [data-related]").forEach((el) => {
      el.innerHTML = `<p class="empty">數據載入失敗（${escapeHTML(error.message)}）。若是直接用檔案開啟，請改用本機伺服器或 GitHub Pages 瀏覽。</p>`;
    });
  });
