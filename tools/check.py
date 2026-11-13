"""NBA 數據小站 規則檢查程式（對應 AGENTS.md）

用法：在專案根目錄執行
    python tools/check.py

只使用 Python 標準函式庫。有錯誤時結束代碼為 1。
"""
import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "NBA 數據小站"

# AGENTS.md 第 5 節：分類與必備區塊
REQUIRED_SECTIONS = {
    "players": ["overview", "stats", "analysis"],
    "teams": ["overview", "stats", "analysis"],
    "topics": ["question", "chart", "findings", "method"],
}
LAST_SECTIONS = ["related", "sources"]

# AGENTS.md 第 4 節：CSV 檔案與欄位
CSV_FILES = {
    "players": ("raw/players_2024-25.csv",
                "id,name,name_zh,team,pos,age,g,mp,pts,trb,ast,stl,blk,tov,fg_pct,fg3_pct,ft_pct,awards"),
    "teams": ("raw/teams_2024-25.csv", "id,name,name_zh,abbr,conf,w,l,pts,opp_pts,srs"),
}
NUMERIC = {
    "players": ["age", "g", "mp", "pts", "trb", "ast", "stl", "blk", "tov", "fg_pct", "fg3_pct", "ft_pct"],
    "teams": ["w", "l", "pts", "opp_pts", "srs"],
}
PERCENT = ["fg_pct", "fg3_pct", "ft_pct"]

# AGENTS.md 第 6 節：可用指標（要和 assets/main.js 的 METRICS 一致）
METRICS = {
    "players": {"pts", "trb", "ast", "stl", "blk", "tov", "mp", "g", "fg_pct", "fg3_pct", "ft_pct"},
    "teams": {"w", "win_pct", "pts", "opp_pts", "net", "srs"},
}
FIELDS = ["id", "title", "category", "path", "summary", "tags", "related", "sources", "updated"]

errors, warnings = [], []


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.body, self.title, self.summary = {}, "", ""
        self.sections, self.links, self.redlinks = [], [], []
        self.tables, self.charts = [], []
        self.inline_style = False
        self._section = None
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if "style" in a or tag == "style":
            self.inline_style = True
        if tag == "body":
            self.body = a
        elif tag == "title":
            self._in = "title"
        elif tag == "section":
            self._section = a.get("id")
            self.sections.append(self._section)
        elif tag == "a" and "wikilink" in cls:
            self.links.append(a.get("href", ""))
        elif tag == "span" and "redlink" in cls:
            self._in = "redlink"
        elif tag == "p" and "summary" in cls:
            self._in = "summary"
        elif tag == "table":
            errors.append(f"[{self.body.get('data-page-id')}] 不要手打 <table>，請用 stat-table 元件")
        if "stat-table" in cls:
            self.tables.append((self._section, a))
        if "bar-chart" in cls:
            self.charts.append((self._section, a))

    def handle_endtag(self, tag):
        if tag in ("title", "span", "p"):
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "summary":
            self.summary += data
        elif self._in == "redlink":
            self.redlinks.append(data.strip())
        # AGENTS.md 第 10 節：不要寫死收錄人數
        if re.search(r"\d+\s*(位球員|人中)", data):
            errors.append(f"[{self.body.get('data-page-id')}] 不要寫死收錄人數：「{data.strip()[:30]}」")


def load_csv():
    data = {}
    for source, (path, header) in CSV_FILES.items():
        file = ROOT / path
        if not file.exists():
            errors.append(f"找不到 {path}")
            data[source] = {}
            continue
        with file.open(encoding="utf-8") as f:
            reader = csv.reader(f)
            head = next(reader)
            if ",".join(head) != header:
                errors.append(f"{path} 的欄位應為：{header}")
            rows = {}
            for n, cells in enumerate(reader, start=2):
                if not cells:
                    continue
                row = dict(zip(head, cells))
                rid = row.get("id", "")
                if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", rid):
                    errors.append(f"{path} 第 {n} 行：id「{rid}」必須是英文小寫加連字號")
                if rid in rows:
                    errors.append(f"{path} 第 {n} 行：id 重複「{rid}」")
                for col in NUMERIC[source]:
                    try:
                        value = float(row.get(col, ""))
                    except ValueError:
                        errors.append(f"{path} 第 {n} 行：{col} 不是數字")
                        continue
                    if col in PERCENT and not 0 <= value <= 1:
                        errors.append(f"{path} 第 {n} 行：{col} 應為 0～1 的小數")
                rows[rid] = row
            data[source] = rows
    return data


def check_page(entry, data):
    pid, cat = entry["id"], entry["category"]
    tag = f"[{pid}]"
    path = ROOT / entry["path"]
    p = PageParser()
    p.feed(path.read_text(encoding="utf-8"))

    if p.body.get("data-page-id") != pid:
        errors.append(f"{tag} <body data-page-id> 應為 {pid}")
    if p.body.get("data-root") != "../../":
        errors.append(f"{tag} <body data-root> 應為 ../../")
    if p.title.strip() != f"{entry['title']}｜{SITE}":
        errors.append(f"{tag} <title> 應為「{entry['title']}｜{SITE}」")
    if p.summary.strip() != entry["summary"]:
        errors.append(f"{tag} 頁面摘要和 pages.json 的 summary 不一致")
    if p.inline_style:
        errors.append(f"{tag} 不可使用 inline style 或 <style>")

    expected = REQUIRED_SECTIONS[cat] + LAST_SECTIONS
    if p.sections != expected:
        errors.append(f"{tag} 區塊順序應為 {expected}，目前是 {p.sections}")

    # 球員、球隊頁：本頁必須在 CSV 中，stats 區塊要有本頁的數據表和至少一張圖
    if cat in ("players", "teams"):
        if pid not in data.get(cat, {}):
            errors.append(f"{tag} CSV 中沒有這個 id，請先新增數據（AGENTS.md 第 4 節）")
        if not any(sec == "stats" and a.get("data-source") == cat and a.get("data-id") == pid for sec, a in p.tables):
            errors.append(f"{tag} stats 區塊需要 <div class=\"stat-table\" data-source=\"{cat}\" data-id=\"{pid}\">")
        if not any(sec == "stats" for sec, _ in p.charts):
            errors.append(f"{tag} stats 區塊至少需要一張 bar-chart")
    if cat == "topics" and not any(sec == "chart" for sec, _ in p.charts):
        errors.append(f"{tag} chart 區塊至少需要一張 bar-chart")

    for sec, a in p.tables:
        src = a.get("data-source")
        if src not in data:
            errors.append(f"{tag} stat-table 的 data-source 只能是 players 或 teams")
        elif a.get("data-id") not in data[src]:
            errors.append(f"{tag} stat-table 的 data-id「{a.get('data-id')}」不在 CSV 中")

    for sec, a in p.charts:
        src, metric = a.get("data-source"), a.get("data-metric")
        if src not in METRICS:
            errors.append(f"{tag} bar-chart 的 data-source 只能是 players 或 teams")
            continue
        if metric not in METRICS[src]:
            errors.append(f"{tag} bar-chart 的指標「{metric}」不能用在 {src}")
        for hid in filter(None, (a.get("data-highlight") or "").split(",")):
            if hid.strip() not in data[src]:
                errors.append(f"{tag} bar-chart 要標示的「{hid}」不在 CSV 中")
        if a.get("data-conf") not in (None, "東區", "西區"):
            errors.append(f"{tag} bar-chart 的 data-conf 只能是 東區 或 西區")
        if a.get("data-order") not in (None, "asc", "desc"):
            errors.append(f"{tag} bar-chart 的 data-order 只能是 asc 或 desc")

    for href in p.links:
        if not (path.parent / href).resolve().exists():
            errors.append(f"{tag} wikilink 連到不存在的頁面：{href}")
    for name in p.redlinks:
        warnings.append(f"[{pid}] 尚未建立頁面（redlink）：{name}")


def main():
    data = load_csv()
    try:
        pages = json.loads((ROOT / "data" / "pages.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"錯誤：無法讀取 data/pages.json（{exc}）")
        return 1

    ids = [p.get("id") for p in pages]
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"pages.json 中的 id 重複：{dup}")
    raw_files = {f.name for f in (ROOT / "raw").glob("*.csv")}
    registered = set()

    for entry in pages:
        missing = [f for f in FIELDS if f not in entry]
        if missing:
            errors.append(f"[{entry.get('id', '?')}] pages.json 缺少欄位：{missing}")
            continue
        pid, tag = entry["id"], f"[{entry['id']}]"
        if entry["category"] not in REQUIRED_SECTIONS:
            errors.append(f"{tag} 未知的分類：{entry['category']}")
            continue
        if entry["path"] != f"wiki/{entry['category']}/{pid}.html":
            errors.append(f"{tag} path 應為 wiki/{entry['category']}/{pid}.html")
        if not (ROOT / entry["path"]).exists():
            errors.append(f"{tag} 找不到檔案：{entry['path']}")
            continue
        registered.add(entry["path"])
        if len(entry["summary"]) > 40:
            errors.append(f"{tag} summary 超過 40 字（{len(entry['summary'])} 字）")
        if not 2 <= len(entry["tags"]) <= 5:
            errors.append(f"{tag} tags 需要 2～5 個")
        if not 2 <= len(entry["related"]) <= 5:
            errors.append(f"{tag} related 需要 2～5 個")
        for rid in entry["related"]:
            if rid == pid or rid not in ids:
                errors.append(f"{tag} related 中的「{rid}」不存在或是自己")
        for src in entry["sources"]:
            if src not in raw_files:
                errors.append(f"{tag} sources 中的「{src}」不在 raw/")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["updated"]):
            errors.append(f"{tag} updated 格式應為 YYYY-MM-DD")
        check_page(entry, data)

    for html in sorted((ROOT / "wiki").rglob("*.html")):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in registered:
            errors.append(f"{rel} 沒有登記在 pages.json")

    print(f"檢查了 {len(pages)} 個頁面、{len(data.get('players', {}))} 位球員、{len(data.get('teams', {}))} 支球隊。")
    if warnings:
        unique = sorted(set(warnings))
        print(f"\n提醒（{len(unique)}）：可以考慮建立的頁面")
        for w in unique:
            print("  -", w)
    if errors:
        print(f"\n錯誤（{len(errors)}）：")
        for e in errors:
            print("  ✗", e)
        return 1
    print("\n✓ 全部通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
