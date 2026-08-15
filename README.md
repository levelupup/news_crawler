# News Crawler

Async news aggregator that crawls ~48 international tech/business sources (59 fetchers, counting OFweek's 11 verticals separately), deduplicates against a local JSONL archive, and writes HTML outputs. An AI analysis layer (`analyze_news.py` / `analyze_india.py`) scores and clusters events using local Ollama models.

This repository publishes **outputs only** — the crawler/analysis code, the full archive and the scraped article bodies stay on the machine that runs them.

## Sources

| Module | Display Name | Method |
|---|---|---|
| `bloomberg.py` | Bloomberg | Google News RSS |
| `reuters.py` | Reuters | Google News RSS |
| `wsj.py` | WSJ | Native RSS |
| `techcrunch.py` | TechCrunch | Native RSS |
| `theinformation.py` | The Information | Google News RSS |
| `cnbc.py` | CNBC Technology | Native RSS |
| `scmp.py` | South China Morning Post | Native RSS |
| `thelec.py` | The Elec | Native RSS |
| `zdkorea.py` | ZDNet Korea | Native RSS（韓文原標題）|
| `36kr.py` | 36kr.com | Google News RSS |
| `nikkei.py` | Nikkei Asia | Native RSS |
| `livemint.py` | Livemint | Native RSS |
| `economictimes.py` | Economic Times | Native RSS |
| `9to5mac.py` | 9to5Mac | Native RSS |
| `appleinsider.py` | AppleInsider | Native RSS |
| `electrek.py` | Electrek | Native RSS |
| `huaweicentral.py` | Huawei Central | Google News RSS |
| `cna.py` | 中央社 | Native RSS |
| `technews.py` | TechNews 科技新報 | Native RSS |
| `businessweekly.py` | 商業周刊 | Native RSS |
| `dramx.py` | DRAMX | Native RSS |
| `udn_money.py` | 經濟日報 | Google News RSS |
| `ctee.py` | 工商時報 | Google News RSS |
| `moneycontrol.py` | Moneycontrol | BeautifulSoup scraping |
| `business_standard.py` | Business Standard | Native RSS（Industry feed；需瀏覽器 UA，feedparser 預設 UA 吃 403） |
| `hindubusinessline.py` | Hindu BusinessLine | Native RSS（Info-Tech feed，站方混入 markets/economy 等版面，實際版面放在 company 欄） |
| `chinaflashmarket.py` | 中國閃存市場 | BeautifulSoup scraping |
| `chinastarmarket.py` | 科創板日報 | BeautifulSoup scraping |
| `c114.py` | C114通信網 | BeautifulSoup scraping |
| `cnevpost.py` | CNEVPost | BeautifulSoup scraping |
| `ifeng.py` | 鳳凰網科技 | BeautifulSoup scraping |
| `justAuto.py` | Just Auto | Native RSS |
| `laoyaoba.py` | 集微網 | Native RSS (small feed, ~10 entries) |
| `ofweek.py` | OFweek (11 verticals) | BeautifulSoup scraping |
|   | - 機器人網 / 人工智能網 / 智能製造網 |  |
|   | - 顯示網 / 雲計算網 / 鋰電網 |  |
|   | - 傳感器網 / 新能源汽車網 / 儲能網 |  |
|   | - 智能硬件網 / 光通訊網 |  |
| `stcn.py` | 證券時報 | AJAX JSON（游標分頁，回傳 HTML 片段） |
| `sina_finance.py` | 新浪財經(個股資訊) | regex scraping（公司清單在 `sina_common.py`，201 家，與公告共用） |
| `sina_bulletin.py` | 新浪財經(公司公告) | regex scraping（同一份清單，扣掉無公告頁的港股/北交所後 193 家；6h 刷新閘門） |
| `india_electronics.py` | India Electronics | 搜尋聚合（非單一站點爬蟲）——`india_search.py` 由獨立 `india_search.timer`（:20/:50）以 GNews RSS／SearXNG／ddgs（＋免費額度內的 Tavily/Brave）搜尋寫入 staging `data/india_electronics.jsonl`，本模組只讀近 48h 條目、不連網。`company` 放發稿媒體的短網域名（`app.dealroom.co`→`dealroom`、`datacenters.economictimes.indiatimes.com`→`indiatimes`）|
| `pib_india.py` | PIB India 印度新聞局 | BeautifulSoup scraping（ASP.NET postback；發稿部會放 company 欄）|
| `eetimes_india.py` | EE Times India | BeautifulSoup scraping |
| `silicon_semiconductor_china.py` | Silicon Semiconductor China | BeautifulSoup scraping |
| `edge_markets.py` | The Edge Malaysia | Next.js `__NEXT_DATA__` JSON |
| `vnexpress.py` | VnExpress | BeautifulSoup scraping |
| `techwireasia.py` | Tech Wire Asia | BeautifulSoup scraping |
| `evertiq.py` | Evertiq | BeautifulSoup scraping |
| `yicai.py` | 第一財經 科創 | BeautifulSoup scraping |
| `guancha.py` | 觀察者網 經濟 | BeautifulSoup scraping |
| `sohu.py` | 搜狐IT | Playwright + stealth |
| `yonhap.py` | Yonhap News | Native RSS |
| `newsis.py` | 뉴시스 Newsis | Native RSS（industry＋economy 兩個版面；**關鍵字閘只留電子業相關**，見下）|
| `chosunbiz.py` | Chosun Biz | Playwright（**逾 7 天的舊文只入庫、不上報表**，見下）|

## Outputs

| File | Description |
|---|---|
| `today.html` | Articles from today + yesterday (filterable by source) |
| `important.html` | AI精選：6h / 12h / 2d / 7d tabs of Ollama-scored top events |
| `grouped.html` | Cross-lingual same-event clusters (≥2 sources) |
| `india.html` | 印度重要新聞：五家印度來源近 2 日、按**產業重要性**排序的 Top 30（`analyze_india.py`，每 12 小時） |
| `analysis.json` | Machine-readable scored event list from the last analysis run |
| `india_analysis.json` | Machine-readable scored event list from the last India analysis run |
| `error_list.html` | Per-source error report from the last run (0-article sources included) |
| `data/recent.csv` | Git-tracked 7-day slice pushed to GitHub (feeds analyze_news.py) |
| `archive/YYYY-MM-DD.jsonl` | Full append-only local archive (git-ignored) |

## Source-level filters

Two sources are noisy in ways a downstream AI score cannot fix, so they are gated at crawl time.

**Newsis — electronics-only keyword gate** (`newsis.is_electronics`). Its industry/economy
RSS feeds are general business wires; a live sample was ~85% food / fashion / retail / hotel
items and a 7-day stored sample kept only ~12%. A title passes if it hits the electronics
vocabulary (半導體/디스플레이/스마트폰/배터리/AI/기업名…) or is policy news (관세·수출통제·
보조금·특별법…) that also carries an industry term and is not another sector's story. Pure
regex — the pool is ~40 titles per run, so an LLM call per title would be all cost.

**Chosun Biz — 7-day staleness gate** (`run_crawlers.STALE_FILTER_DOMAINS`). Its English IT
section mixes months-old features into the listing (672 of 2228 stored articles, 30%). The
publication date is parsed from the article URL (`/en/en-it/2026/08/15/…`); anything older
than `STALE_AFTER_DAYS` (7) is still crawled, archived, exported to `data/recent.csv` and
body-scraped — the corpus wants it — but is flagged `stale` and therefore **omitted from
today.html and from the analyze_news / analyze_india input**, because ranking a 3-month-old
headline as news distorts important.html. The flag travels to the analysis step through
`data/stale_urls.json`, since recent.csv has no column for it.

## AI Analysis (`analyze_news.py`)

Reads `data/recent.csv`, clusters headlines by semantic similarity, then scores with local Ollama models. Runs independently of `run_crawlers.py`.

**Pipeline:**

1. **Stage 1 — Keyword filter**: hard-drop 股價 titles; remove obvious market noise (盤中/漲停/匯率/期貨…)
2. **Stage 2 — Embed + cluster**: `embeddinggemma:300m` vectors → cosine agglomerative clustering → cross-lingual same-event super-merge. (2026-07-04 benchmarked vs qwen3-embedding 0.6b/4b/8b on real bodies: gemma is the only model ranking cross-lingual same-story pairs above same-day different-company pairs — do NOT switch this to qwen.)
3. **Stage 3 — Prescreen**: `qwen3.6:35b-a3b` tags each cluster as tech/non-tech + coarse score
4. **Stage 4 — Score + name**: `qwen3.6:35b-a3b` assigns a Traditional Chinese headline and a precise 0–100 importance score, then `merge_same_name_events` collapses events named identically/near-identically (fixes the recurring "IBM ranked #6 and #10 with the same headline" false splits — root cause was size-1 clusters missing the merge candidate set, not embedding quality)

**Scoring criteria (applied cumulatively):**

| Factor | Rule |
|---|---|
| **Source authority** | +8 for Reuters / WSJ / Bloomberg / The Information / Nikkei Asia / 第一財經 / 科創板日報 / The Elec |
| | −5 for OFweek outlets |
| **Exclusivity** | +5 if title contains 獨家 / 独家 / exclusive / 首發 |
| **Event specificity** | +5 for concrete subject+verb events; −5 for pure commentary / outlook |
| **Company tier** | +5 if involves TSMC / Samsung / NVIDIA / Apple / Intel / Qualcomm / ASML / SK Hynix / Micron / Huawei / MediaTek / AMD / Microsoft / Google / Meta / Amazon / Tesla / BYD / SMIC |
| **Topic category** | +8 for semiconductor / AI (晶片設計、晶圓廠、封裝、GPU/NPU、LLM、半導體設備/材料、記憶體、AI 基礎設施) |
| | +4 for electronics manufacturing / assembly / components (EMS/ODM 代工、PCB/基板、MLCC、連接器、鏡頭模組、面板、PMIC、FPC) |
| | 0 for all other topics (軟體平台、消費 App、一般總經) |

**`important.html` tabs (default: 近 6 小時):**
- **⚡ 近 6 小時 Top 15** — events whose latest article appeared within the past 6 hours
- **🕐 近 12 小時 Top 30** — events from the past 12 hours
- **📋 近 2 日 Top 30** — events from the past 2 days
- **📅 近 7 日 Top 30** — all scored events from the past 7 days (full analysis window)

## India Analysis (`analyze_india.py`)

同一套分群/嵌入程式碼（直接 `import analyze_news`），換來源、換評分準則，輸出 `india.html`。

- **來源**：Business Standard、Hindu BusinessLine、Moneycontrol、Livemint、India Electronics
- **視窗**：近 2 日 ｜ **頻度**：每 12 小時（`news_analyze_india.timer`，10:00 / 22:00 TW，配合早晚新聞作業）
- **只評產業重要性單一分數**——沒有讀者關注度／四種 persona，所以頁面沒有排序切換鈕
- **評分準則**：對印度電子／半導體／製造業與其供應鏈的重要性。加權：半導體/顯示晶圓廠・封測・
  晶片設計・AI 算力建置 +8；EMS/ODM 建廠・PLI 等零組件方案・手機與 IT 硬體組裝 +6；
  汽車電子・電信設備・國防電子等鄰接產業 +3；IT 服務／軟體 0。另有「具體已承諾事件 +5／
  空泛展望 −5」、「大額投資或一線業者 +5」、「中央政策決定 +5／僅表態 −3」。
  股市行情、財報行事曆、銀行保險、消費生活、與產業無關的政治 = 0 分。
- **報導媒體欄**：四家單一站台顯示媒體名；India Electronics 是聚合器，改用各篇 URL 推出的
  短網域名（`dealroom`、`pmindia`、`indiatimes`），同一事件下不同發稿媒體各留一條連結。

## Setup

```bash
python -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/playwright install chromium
```

## Usage

Always call the venv interpreter directly (`venv/bin/python …`) rather than activating it —
on the host that runs this, a conda base env shadows the venv's `pip`.

```bash
# Run all crawlers (writes today.html + data/recent.csv)
venv/bin/python run_crawlers.py

# Run AI analysis (writes important.html + grouped.html + analysis.json)
venv/bin/python analyze_news.py

# India-only ranking (writes india.html + india_analysis.json)
venv/bin/python analyze_india.py --days 2

# Test a single crawler
venv/bin/python reuters.py
venv/bin/python newsis.py
# (any crawler module supports direct execution)
```

## Architecture

`run_crawlers.py` dynamically imports all crawler modules via `importlib`, runs them concurrently with `asyncio` + `ThreadPoolExecutor` (16 workers), deduplicates against the full JSONL archive, and writes HTML + CSV outputs.

Each crawler module returns `list[dict]` with `title` + `url` (plus optional `company` /
`published`); `run_crawlers._wrap` adds `domain` and `crawled_at` and is where the staleness
flag is set.

Korean sources (ZDNet Korea, Newsis, Yonhap) keep their **original Korean titles**. The
crawl-time Ollama translation was dropped in 2026-07 to spare GPU time — translate in-browser
instead.
