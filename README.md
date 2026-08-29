# News Crawler

Async news aggregator that crawls ~48 international tech/business sources (59 fetchers, counting OFweek's 11 verticals separately), deduplicates against a local JSONL archive, and writes HTML outputs. An AI analysis layer (`analyze_news.py` / `analyze_india.py` / `analyze_china.py` / `analyze_ai.py` + `analyze_semi.py`) scores and clusters events using local Ollama models.

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
| `important.html` | 重要科技新聞：6h / 12h / 2d / 7d tabs of Ollama-scored top events |
| `grouped.html` | Cross-lingual same-event clusters (≥2 sources) |
| `ai.html` | AI 重要新聞：**全部來源**近 2 日、模型／軟體側的 Top 18，依同性質分組後重要性降冪（`analyze_ai.py`，每 4 小時） |
| `semiconductor.html` | 半導體重要新聞：**全部來源**近 2 日的 Top 18，依價值鏈環節分組後重要性降冪（`analyze_semi.py`，每 4 小時） |
| `india.html` | 印度重要新聞：五家印度來源近 2 日、按**產業重要性**排序的 Top 18（`analyze_india.py`，每 12 小時） |
| `china.html` | 中國重要新聞：12 家中國來源近 2 日、按**產業重要性**排序的 Top 18，國產替代／科技自主／降低外依／半導體加權（`analyze_china.py`，每 12 小時） |
| `analysis.json` | Machine-readable scored event list from the last analysis run |
| `ai_analysis.json` | Machine-readable scored event list from the last AI analysis run |
| `semi_analysis.json` | Machine-readable scored event list from the last semiconductor analysis run |
| `india_analysis.json` | Machine-readable scored event list from the last India analysis run |
| `china_analysis.json` | Machine-readable scored event list from the last China analysis run |
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

## Topic Analysis (`analyze_ai.py` / `analyze_semi.py`，共用 `analyze_topic.py`)

india/china 是**地域型**報告（來源固定成該國那幾家，主題不限）；ai/semiconductor 是**主題型**
報告（來源涵蓋 `recent.csv` 全部 60+ 家，改由 prescreen 的主題閘門決定誰進得來）。兩份主題報告的
管線一模一樣，所以不再各複製一份殼——整條管線收在 `analyze_topic.py`，`analyze_ai.py` /
`analyze_semi.py` 只提供一份 `TopicSpec`（主題閘門 prompt、評分準則、分組清單）。分群與嵌入
仍全部沿用 `analyze_news` 的同一套函式。

共通設計：

- **視窗**：近 2 日 ｜ **清單長度**：Top 18（四份報告一致）
- **頻度**：每 4 小時，兩份錯開 2 小時 —— AI 在 01:45/05:45/09:45/13:45/17:45/21:45，
  半導體在 03:45/07:45/11:45/15:45/19:45/23:45（TW）。單次約 10-12 分鐘，兩份永遠不會同時
  壓 579a 的 GPU。**為什麼是 :45**：`data/recent.csv` 被 `news_crawler` 在 :00/:30 以
  非原子方式重寫（`write_recent_slice` 用 `"w"` 開檔），:45 遠離兩個寫入窗、又吃得到 :30 那批，
  是最新鮮的安全讀取點；讀到寫入中的檔會**靜默**得到一份薄報告而不是錯誤，所以這兩個 timer
  和 india/china 一樣刻意不設 `RandomizedDelaySec`。
- **Stage 1 中文關鍵字過濾要跑**（同 `analyze_china` 的理由，來源含大量簡中財經稿）：沿用
  `analyze_news` 的 `_HARD_DROP_RE`/`_ROUTINE_RE`/`_NOISE_RE`，外加 `analyze_topic._FILING_RE`
  擋純例行公告（與 `analyze_china._FILING_RE` 同一條，改一邊要改兩邊）。
  實測 4190 → 3018 則（股價 27／行情雜訊 756／例行公告 389）。
- **分組**：精評時模型除了分數還要從 spec 的固定清單挑一個 `group`，清單外的自創標籤一律收進
  「其他」（放行會讓同一類新聞散成三段）。版面是「一組一段」：段落之間依該組最高分排序、
  段落之內依分數排序，每列的 `#` 是**全表名次**不是組內名次，所以「哪一類重要」和「整體第幾重要」
  在同一張表上都讀得出來。
- **輸出一律繁體**：來源同時有英文與簡體中文，模型講完再過一次 OpenCC `s2twp`（同 `analyze_china`
  的理由與作法）。

`ai.html` — 偏**模型／軟體側**：競爭動態與市場格局、AI 實驗室與模型新創的集資、模型與產品發布。
刻意收進來的是**模型業者自己推出的硬體**（例如 OpenAI 的裝置）；刻意排除純晶片供應鏈新聞。
分組：模型與產品發布／競爭格局與合作結盟／集資與估值／算力採購與基礎設施／硬體產品／人才與組織／
監理與法規。加權：前沿能力躍進 +10、競爭態勢改變 +8、資本規模（≥US$1B）+8、具體已承諾 +5／
傳聞展望 −5、開源或大幅降價擴大可及性 +4、具拘束力的法規 +5／僅表態 −3。

`semiconductor.html` — 涵蓋半導體 IP、IC 設計、晶圓代工、封裝測試、IDM、記憶體、半導體技術
（製程／設備／材料／EDA）。分組按**價值鏈環節**：晶圓代工／記憶體／IC 設計與 IP／EDA／封裝測試／
IDM 與整合元件／設備與材料／製程與技術突破／政策、貿易與資本動作。加權：技術領先里程碑 +10、
產能與供給 +8、供應鏈重新洗牌（design win、換供應商、通過認證）+7、具拘束力的貿易與政策 +6／
僅表態 −3、大額資本（≥US$1B）+5、具體已承諾 +5／傳聞展望 −5。

**兩頁與 important.html／china.html 重疊是預期的**——不同鏡頭看同一件事本來就該各留一則。
邊界規則：主角是晶片業者 → semiconductor；主角是模型業者 → ai。

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

## China Analysis (`analyze_china.py`)

和 `analyze_india.py` 一樣是 `analyze_news` 的薄殼（直接 `import analyze_news`，分群/嵌入/合併共用），
換來源、換評分準則，輸出 `china.html`。

- **來源（12 家，使用者指定）**：36kr.com、新浪財經(個股資訊)、SCMP、鳳凰網科技、科創板日報、
  Huawei Central、證券時報、第一財經 科創、集微網、觀察者網 經濟、新浪財經(公司公告)、OFweek。
  OFweek 在 `recent.csv` 是 11 個 `ofweek_*` 分站 domain，`analyze_china._domain_group()` 把它們
  收成一個（與 `run_crawlers._display_domain` 同規則，改一邊要改兩邊）。
- **視窗**：近 2 日 ｜ **頻度**：每 12 小時（`news_analyze_china.timer`，10:30 / 22:30 TW —— 排在
  印度報告後半小時，兩份報告不同時壓 579a 的 GPU）
- **與印度版最大的差別：Stage 1 中文關鍵字過濾要跑。** 印度來源全英文，`analyze_news` 的中文正則
  命中率 0 所以跳過；中國來源反過來，不跑這層新浪的行情與例行公告會淹掉整個池子。除了沿用
  `_HARD_DROP_RE`/`_ROUTINE_RE`/`_NOISE_RE`，另有 `analyze_china._FILING_RE` 擋純例行公告
  （半年報、董事會決議、股東會通知、限制性股票…）。實測 684 → 422 則，其中公司公告 69 → 3，
  且對 36kr/鳳凰/證券時報等新聞來源 0 誤刪。加字進 `_FILING_RE` 的規矩：只收「只可能出現在樣板
  公告裡」的詞，擴產／投資建設／重大合同／定增募資這類實質經營動作一律不准進去。
- **只評產業重要性單一分數**——沒有讀者關注度／四種 persona，所以頁面沒有排序切換鈕
- **評分加權（使用者指定的四軸最重）**：國產替代／自主可控 +12；半導體（晶圓廠・先進封裝・記憶體・
  設備材料・EDA・晶片設計）+10；降低對外依賴（出口管制、實體清單、稀土槓桿、被迫在地化）+8；
  其後才是 AI 算力 +6／電子製造 +5／鄰接工業 +3／網路平台 0。另有「具體已承諾事件 +5／空泛展望 −5」、
  「大額投資或一線業者 +5」、「中央政策決定 +5／僅表態 −3」。
  股市行情、例行公告、財報行事曆、銀行保險地產、消費生活、與產業無關的政治 = 0 分。
- **主題標籤**：模型從 `ALLOWED_TAGS` 固定清單挑 0-3 個掛在事件下（集合外的自創標籤一律丟棄，
  否則同一件事會出現三種寫法）；四個加權軸用藍底色塊突顯，其餘灰底。
- **輸出一律繁體**：來源大多是簡體，prompt 明確要求轉繁並禁止簡體字——不明講的話模型會直接吐簡體。

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

# China-only ranking (writes china.html + china_analysis.json)
venv/bin/python analyze_china.py --days 2
# Stage 1 filter counts only — no LLM, no GPU, no output files
venv/bin/python analyze_china.py --dry-run

# Topic reports over ALL sources (writes ai.html / semiconductor.html + their JSON)
venv/bin/python analyze_ai.py --days 2
venv/bin/python analyze_semi.py --days 2
venv/bin/python analyze_ai.py --dry-run      # Stage 1 counts only, no LLM

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
