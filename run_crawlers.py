"""
run_crawlers.py — Master async news crawler.

Runs all 16 source crawlers concurrently, deduplicates against stored history,
writes local HTML + per-domain CSV files, and syncs to Google Sheets.

Usage:
    python run_crawlers.py
"""

import asyncio
import csv
import importlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
sys.path.insert(0, str(BASE_DIR))

HTML_LATEST  = BASE_DIR / "news_crawler_latest.html"
HTML_TODAY   = BASE_DIR / "today.html"

TW_TZ = timezone(timedelta(hours=8))

TODAY_DATE     = datetime.now(TW_TZ).strftime("%Y-%m-%d")
YESTERDAY_DATE = (datetime.now(TW_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")

CRAWLED_AT = datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S")

# ── Domain slug → display name ────────────────────────────────────────────────
DOMAINS = {
    "36kr":             "36kr.com",
    "bloomberg":        "Bloomberg",
    "c114":             "C114通信網",
    "chinaflashmarket": "中國閃存市場",
    "economictimes":    "Economic Times",
    "einnews":          "EIN News",
    "ifeng":            "鳳凰網科技",
    "livemint":         "Livemint",
    "moneycontrol":     "Moneycontrol",
    "nikkei":           "Nikkei Asia",
    "reuters":          "Reuters",
    "sina_finance":     "新浪財經",
    "sohu":             "搜狐IT",
    "techcrunch":       "TechCrunch",
    "theinformation":   "The Information",
    "wsj":              "WSJ",
}

CSV_COLUMNS = ["domain", "company", "title", "url", "crawled_at"]


# ── Inline fetchers for legacy scripts (module-level side-effects prevent import) ──

def _fetch_einnews() -> list[dict]:
    countries    = ["india"]
    ein_domains  = ["electriccars", "semiconductors", "cellphones", "tech", "solarenergy", "electronics"]
    articles: list[dict] = []
    for dm in ein_domains:
        for ctry in countries:
            url      = f"https://{dm}.einnews.com/country/{ctry}"
            root_url = f"https://{dm}.einnews.com"
            try:
                r    = requests.get(url, timeout=15)
                soup = BeautifulSoup(r.text, "lxml")
                for h in soup.find_all("a", {"class": "title"}):
                    href  = h.get("href", "")
                    title = h.text.strip()
                    if not href or not title:
                        continue
                    href = href[: href.find("?")] if "?" in href else href
                    href = f"{root_url}{href}" if "https://" not in href else href
                    articles.append({"company": "", "title": title, "url": href})
            except Exception as exc:
                print(f"  [einnews] {dm}/{ctry}: {exc}")
    return articles


_SINA_URLS = {
    "立訊":    "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002475.phtml",
    "歌爾":    "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002241.phtml",
    "聞泰":    "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600745.phtml",
    "環旭電子": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh601231.phtml",
    "華勤技術": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603296.phtml",
    "冠捷科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz000727.phtml",
    "藍思":    "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300433.phtml",
    "摩爾線程": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688795.phtml",
    "晶合集成": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688249.phtml",
    "中芯國際": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688981.phtml",
    "通富微電": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002156.phtml",
    "長電科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600584.phtml",
    "華天科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002185.phtml",
    "格科微":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688728.phtml",
    "韋爾股份": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603501.phtml",
    "豪威集團": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600460.phtml",
    "華潤微":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688396.phtml",
    "華微電子": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600360.phtml",
    "國民技術": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300077.phtml",
    "兆易創新": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603986.phtml",
    "瀾起科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688008.phtml",
    "北方華創": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002371.phtml",
    "晶盛機電": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300316.phtml",
    "中微半導體": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688012.phtml",
    "至純科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh6039690.phtml",
    "盛美上海": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688082.phtml",
    "拓荊科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688072.phtml",
    "華海清科": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688120.phtml",
    "芯源微":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688037.phtml",
    "納芯微":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688052.phtml",
    "景嘉微":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300474.phtml",
    "海光信息": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688041.phtml",
    "太極實業": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600667.phtml",
    "深科技":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz000021.phtml",
    "華大九天": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz301269.phtml",
    "中科飛測": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688361.phtml",
    "滬矽產業": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688126.phtml",
    "概倫電子": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688206.phtml",
    "長川科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300604.phtml",
    "南大光電": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300346.phtml",
    "安集科技": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688019.phtml",
    "華峰測控": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688200.phtml",
    "國軒高科": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002074.phtml",
    "寧德時代": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300750.phtml",
    "比亞迪":   "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002594.phtml",
    "億緯鋰能": "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300014.phtml",
    "華虹":    "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688347.phtml",
    "士蘭微":  "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600460.phtml",
}

_SINA_RE_BLOCK = re.compile(r'datelist"><ul>(.*?)</ul>', re.S)
_SINA_RE_ITEM  = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}.*?</a>)', re.S)
_SINA_RE_URL   = re.compile(r"(https?://[^']+)'")
_SINA_RE_TITLE = re.compile(r">(.*?)<")


def _fetch_sina_finance() -> list[dict]:
    import time
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    articles: list[dict] = []
    _blocked = False
    for company, url in _SINA_URLS.items():
        if _blocked:
            break
        try:
            r = session.get(url, timeout=10)
            if r.status_code == 456:
                print(f"  [sina_finance] IP blocked (HTTP 456) — will retry in ~5 min")
                _blocked = True
                break
            block = _SINA_RE_BLOCK.findall(r.text)
            if not block:
                continue
            text = block[0].replace("&nbsp;", " ").strip()
            for item in _SINA_RE_ITEM.findall(text):
                try:
                    link  = _SINA_RE_URL.findall(item)[0]
                    title = _SINA_RE_TITLE.findall(item)[0]
                    articles.append({"company": company, "title": title, "url": link})
                except Exception:
                    pass
        except Exception as exc:
            print(f"  [sina_finance] {company}: {exc}")
        time.sleep(1)
    return articles


# ── URL normalization ──────────────────────────────────────────────────────────

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "source", "from", "cmpid", "cmp",
}

def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url
    params = {k: v for k, v in parse_qs(parsed.query, keep_blank_values=True).items()
              if k.lower() not in _TRACKING_PARAMS}
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))


# ── Normalize raw articles to standard record ──────────────────────────────────

def _wrap(domain: str, raw: list[dict]) -> list[dict]:
    out = []
    for a in raw:
        url   = _normalize_url(a.get("url", "").strip())
        title = a.get("title", "").strip()
        if not url or not title:
            continue
        out.append({
            "domain":     domain,
            "company":    a.get("company", ""),
            "title":      title,
            "url":        url,
            "crawled_at": CRAWLED_AT,
        })
    return out


# ── History helpers ────────────────────────────────────────────────────────────

def _csv_path(domain: str) -> Path:
    return DATA_DIR / f"{domain}.csv"


def load_known_urls() -> set[str]:
    """Collect all previously saved URLs from all domain CSVs."""
    known: set[str] = set()
    for csv_file in DATA_DIR.glob("*.csv"):
        try:
            with open(csv_file, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    if row.get("url"):
                        known.add(row["url"])
        except Exception as exc:
            print(f"  [history] {csv_file.name}: {exc}")
    return known


def load_known_keys() -> set[tuple[str, str]]:
    """Return set of (domain, normalized_title) for same-domain duplicate detection."""
    keys: set[tuple[str, str]] = set()
    for csv_file in DATA_DIR.glob("*.csv"):
        try:
            with open(csv_file, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    d = row.get("domain", "")
                    t = row.get("title", "").strip().lower()
                    if d and t:
                        keys.add((d, t))
        except Exception as exc:
            print(f"  [history] {csv_file.name}: {exc}")
    return keys


def load_all_history() -> list[dict]:
    """Return all historical records from all domain CSVs."""
    records: list[dict] = []
    for csv_file in DATA_DIR.glob("*.csv"):
        try:
            with open(csv_file, encoding="utf-8-sig", newline="") as f:
                records.extend(csv.DictReader(f))
        except Exception as exc:
            print(f"  [history] {csv_file.name}: {exc}")
    return records


def save_new_records(new_records: list[dict]) -> None:
    """Append new records to per-domain CSVs, sorted by crawled_at desc."""
    by_domain: dict[str, list[dict]] = {}
    for rec in new_records:
        by_domain.setdefault(rec["domain"], []).append(rec)

    for domain, recs in by_domain.items():
        path = _csv_path(domain)
        existing: list[dict] = []
        if path.exists():
            with open(path, encoding="utf-8-sig", newline="") as f:
                existing = list(csv.DictReader(f))
        combined = existing + recs
        combined.sort(key=lambda r: r.get("crawled_at", ""), reverse=True)
        cutoff   = (datetime.now(TW_TZ) - timedelta(days=90)).strftime("%Y-%m-%d")
        combined = [r for r in combined if r.get("crawled_at", "")[:10] >= cutoff]
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(combined)
        print(f"  [csv] {path.name}: {len(combined)} total rows ({len(recs)} new)")


# ── HTML output ────────────────────────────────────────────────────────────────

_HTML_STYLE = """\
<style>
  body  { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; }
  h1    { color: #333; margin-bottom: 4px; }
  p.meta{ color: #666; font-size: .9em; margin-top: 0; }
  .filter-bar { margin: 12px 0 8px; display: flex; flex-wrap: wrap; gap: 6px; }
  .filter-btn {
    padding: 4px 12px; border: 1px solid #bbb; border-radius: 14px;
    background: #fff; cursor: pointer; font-size: .85em; color: #444;
    transition: background .15s, color .15s;
  }
  .filter-btn:hover { background: #e0e0f0; }
  .filter-btn.active { background: #4466cc; color: #fff; border-color: #4466cc; }
  p.count { font-size: .85em; color: #666; margin: 4px 0 8px; }
  table { width: 100%; border-collapse: collapse; margin-top: 4px; }
  th    { background: #e8e8f0; padding: 10px; text-align: left;
          border-bottom: 2px solid #ccc; white-space: nowrap; }
  td    { padding: 7px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
  tr:hover { background: #f0f0fa; }
  a     { color: #0066cc; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .domain  { font-size: .82em; color: #555; white-space: nowrap; }
  .company { font-size: .88em; color: #333; white-space: nowrap; }
  .ts      { font-size: .78em; color: #888; white-space: nowrap; }
  .peer-link {
    position: fixed; top: 0.8rem; right: 1rem;
    background: #4466cc; color: #fff !important;
    padding: 0.3rem 0.8rem; border-radius: 4px;
    text-decoration: none !important; font-size: .85em; z-index: 100;
  }
  .peer-link:hover { background: #2244aa; }
</style>"""

_FILTER_JS = """\
<script>
(function(){
  var current = 'all';
  function applyFilter(domain) {
    current = domain;
    document.querySelectorAll('.filter-btn').forEach(function(btn){
      btn.classList.toggle('active', btn.dataset.domain === domain);
    });
    var rows = document.querySelectorAll('tbody tr');
    var visible = 0;
    rows.forEach(function(tr){
      var show = domain === 'all' || tr.dataset.domain === domain;
      tr.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    document.getElementById('row-count').textContent = visible.toLocaleString() + ' articles';
  }
  document.querySelectorAll('.filter-btn').forEach(function(btn){
    btn.addEventListener('click', function(){ applyFilter(btn.dataset.domain); });
  });
  applyFilter('all');
})();
</script>"""


def _html_rows(records: list[dict]) -> str:
    rows = []
    for r in records:
        domain  = r.get("domain", "")
        label   = DOMAINS.get(domain, domain)
        company = r.get("company", "")
        title   = r.get("title", "").replace("<", "&lt;").replace(">", "&gt;")
        url     = r.get("url", "")
        ts      = r.get("crawled_at", "")
        rows.append(
            f'<tr data-domain="{domain}">'
            f'<td class="domain">{label}</td>'
            f'<td class="company">{company}</td>'
            f'<td><a href="{url}" target="_blank">{title}</a></td>'
            f'<td class="ts">{ts}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def _filter_buttons(records: list[dict]) -> str:
    seen = []
    for r in records:
        d = r.get("domain", "")
        if d and d not in seen:
            seen.append(d)
    buttons = ['<button class="filter-btn active" data-domain="all">All</button>']
    for d in seen:
        label = DOMAINS.get(d, d)
        buttons.append(f'<button class="filter-btn" data-domain="{d}">{label}</button>')
    return "\n  ".join(buttons)


def write_html(path: Path, heading: str, records: list[dict],
               filterable: bool = False, peer_link: tuple | None = None) -> None:
    filter_section = ""
    if filterable and records:
        filter_section = f"""
  <div class="filter-bar">
  {_filter_buttons(records)}
  </div>
  <p class="count"><span id="row-count"></span></p>"""

    peer_anchor = ""
    if peer_link:
        href, label = peer_link
        peer_anchor = f'\n  <a class="peer-link" href="{href}">{label}</a>'

    body = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>{heading}</title>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','GTM-WHBV3BXD');</script>
  <!-- End Google Tag Manager -->
  {_HTML_STYLE}
</head>
<body>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WHBV3BXD"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->
{peer_anchor}
  <h1>{heading}</h1>
  <p class="meta">Generated: {CRAWLED_AT} &nbsp;|&nbsp; {len(records):,} articles</p>{filter_section}
  <table>
    <thead>
      <tr><th>Domain</th><th>Company</th><th>Title</th><th>Crawled At</th></tr>
    </thead>
    <tbody>
{_html_rows(records)}
    </tbody>
  </table>
{_FILTER_JS if filterable else ""}
</body>
</html>"""
    path.write_text(body, encoding="utf-8")
    print(f"  [html] {path.name} — {len(records):,} rows")


# ── Async runner ───────────────────────────────────────────────────────────────

async def _run_all() -> list[dict]:
    m36kr  = importlib.import_module("36kr")
    mbl    = importlib.import_module("bloomberg")
    mc114  = importlib.import_module("c114")
    mcfm   = importlib.import_module("chinaflashmarket")
    met    = importlib.import_module("economictimes")
    mifeng = importlib.import_module("ifeng")
    mlm    = importlib.import_module("livemint")
    mmc    = importlib.import_module("moneycontrol")
    mnk    = importlib.import_module("nikkei")
    mreu   = importlib.import_module("reuters")
    msohu  = importlib.import_module("sohu")
    mtc    = importlib.import_module("techcrunch")
    mti    = importlib.import_module("theinformation")
    mwsj   = importlib.import_module("wsj")

    # Map: domain key → zero-arg callable returning raw list[dict]
    # sohu uses asyncio.run() internally; running in a thread is safe because
    # each thread gets its own event loop.
    fetch_tasks: dict[str, object] = {
        "36kr":             lambda: m36kr.fetch_36kr(50),
        "bloomberg":        lambda: mbl.fetch_bloomberg(150),
        "c114":             lambda: mc114.fetch_c114(50),
        "chinaflashmarket": lambda: mcfm.fetch_chinaflashmarket(50),
        "economictimes":    lambda: met.fetch_economictimes(50),
        "einnews":          _fetch_einnews,
        "ifeng":            lambda: mifeng.fetch_ifeng(50),
        "livemint":         lambda: mlm.fetch_livemint(50),
        "moneycontrol":     lambda: mmc.fetch_moneycontrol(50),
        "nikkei":           lambda: mnk.fetch_nikkei_tech(50),
        "reuters":          lambda: mreu.fetch_reuters_technology(50),
        "sina_finance":     _fetch_sina_finance,
        "sohu":             lambda: msohu.fetch_sohu(50),
        "techcrunch":       lambda: mtc.fetch_techcrunch(50),
        "theinformation":   lambda: mti.fetch_theinformation(50),
        "wsj":              lambda: mwsj.fetch_wsj_technology(50),
    }

    loop     = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=16)

    # Returns (records, error_info_or_None)
    async def run_one(domain: str, fn) -> tuple[list[dict], dict | None]:
        try:
            print(f"  [{domain}] fetching…")
            raw = await loop.run_in_executor(executor, fn)
            normalized = _wrap(domain, raw)
            print(f"  [{domain}] {len(normalized)} articles")
            if len(normalized) == 0:
                return [], {
                    "domain": domain,
                    "error": "Returned 0 articles (possible block or empty feed)",
                    "crawled_at": CRAWLED_AT,
                }
            return normalized, None
        except Exception as exc:
            print(f"  [{domain}] ERROR: {exc}")
            return [], {
                "domain": domain,
                "error": str(exc),
                "crawled_at": CRAWLED_AT,
            }

    results = await asyncio.gather(
        *[run_one(d, fn) for d, fn in fetch_tasks.items()]
    )
    executor.shutdown(wait=False)

    all_records: list[dict] = []
    errors: list[dict] = []
    for records, err in results:
        all_records.extend(records)
        if err:
            errors.append(err)
    return all_records, errors


# ── Error HTML ────────────────────────────────────────────────────────────────

HTML_ERRORS = BASE_DIR / "error_list.html"


def write_error_html(errors: list[dict]) -> None:
    if errors:
        rows = "\n".join(
            f'<tr>'
            f'<td class="domain">{DOMAINS.get(e["domain"], e["domain"])}</td>'
            f'<td class="err">{e["error"]}</td>'
            f'<td class="ts">{e["crawled_at"]}</td>'
            f'</tr>'
            for e in errors
        )
        status_badge = f'<span class="badge err-badge">{len(errors)} error(s)</span>'
    else:
        rows = '<tr><td colspan="3" style="text-align:center;color:#888;">No errors</td></tr>'
        status_badge = '<span class="badge ok-badge">All OK</span>'

    body = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>News Crawler — Error List</title>
  {_HTML_STYLE}
  <style>
    .badge      {{ display:inline-block; padding:3px 10px; border-radius:4px;
                   font-size:.85em; font-weight:bold; margin-left:10px; }}
    .err-badge  {{ background:#fdd; color:#a00; }}
    .ok-badge   {{ background:#dfd; color:#060; }}
    .err        {{ color:#c00; font-size:.9em; }}
  </style>
</head>
<body>
  <h1>News Crawler — Error List {status_badge}</h1>
  <p class="meta">Generated: {CRAWLED_AT}</p>
  <table>
    <thead>
      <tr><th>Domain</th><th>Error</th><th>Crawled At</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>"""
    HTML_ERRORS.write_text(body, encoding="utf-8")
    print(f"  [html] {HTML_ERRORS.name} — {len(errors)} error(s)")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"[{CRAWLED_AT}] Starting all crawlers…\n")

    # 1. Fetch concurrently
    fetched, errors = asyncio.run(_run_all())
    print(f"\nFetched total: {len(fetched)} articles  |  Errors: {len(errors)}")

    # 2. Deduplicate against stored history
    known_urls  = load_known_urls()
    known_keys  = load_known_keys()
    new_records = [
        r for r in fetched
        if r["url"]
        and r["url"] not in known_urls
        and (r["domain"], r.get("title", "").strip().lower()) not in known_keys
    ]
    print(f"New (not in history): {len(new_records)} articles\n")

    # Always write error report
    print("\nWriting error report…")
    write_error_html(errors)

    if not new_records:
        print("No new articles — refreshing Today HTML.")
        write_html(HTML_LATEST, "News Crawler — Latest", [], filterable=True,
                   peer_link=("./today.html", "→ Today"))
        history_records = load_all_history()
        today_records   = sorted(
            [r for r in history_records if r.get("crawled_at", "")[:10] in {TODAY_DATE, YESTERDAY_DATE}],
            key=lambda r: r.get("crawled_at", ""), reverse=True,
        )
        write_html(HTML_TODAY, f"News Crawler — 近兩日 ({YESTERDAY_DATE} ~ {TODAY_DATE})", today_records, filterable=True,
                   peer_link=("./news_crawler_latest.html", "→ Latest"))
        return

    # Sort new items by crawled_at desc (all same timestamp, so order = fetch order)
    new_sorted = sorted(new_records, key=lambda r: r["crawled_at"], reverse=True)

    # 3. Persist to per-domain CSVs
    print("Saving CSVs…")
    save_new_records(new_sorted)

    # 4. Write HTML files
    print("\nWriting HTML…")
    write_html(HTML_LATEST, "News Crawler — Latest", new_sorted, filterable=True,
               peer_link=("./today.html", "→ Today"))

    history_records = load_all_history()
    all_sorted      = sorted(history_records, key=lambda r: r.get("crawled_at", ""), reverse=True)
    today_records   = [r for r in all_sorted if r.get("crawled_at", "")[:10] in {TODAY_DATE, YESTERDAY_DATE}]
    write_html(HTML_TODAY, f"News Crawler — 近兩日 ({YESTERDAY_DATE} ~ {TODAY_DATE})", today_records, filterable=True,
               peer_link=("./news_crawler_latest.html", "→ Latest"))

    print(f"\nDone. {len(new_records)} new articles saved.")


if __name__ == "__main__":
    main()
