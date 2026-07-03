# News Crawler

Async news aggregator that crawls 58+ international tech/business sources, deduplicates against a local JSONL archive, and writes HTML outputs. An optional AI analysis layer (`analyze_news.py`) scores and clusters events using local Ollama models.

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
| `zdkorea.py` | ZDNet Korea | Native RSS · titles translated Korean→zh-TW via Ollama |
| `36kr.py` | 36kr.com | Google News RSS |
| `nikkei.py` | Nikkei Asia | Native RSS |
| `nytimes.py` | NYT中文網 | Native RSS |
| `livemint.py` | Livemint | Native RSS |
| `economictimes.py` | Economic Times | Native RSS |
| `9to5mac.py` | 9to5Mac | Native RSS |
| `appleinsider.py` | AppleInsider | Native RSS |
| `electrek.py` | Electrek | Native RSS |
| `huaweicentral.py` | Huawei Central | Google News RSS |
| `cna.py` | 中央社 | Native RSS |
| `technews.py` | TechNews 科技新報 | Native RSS |
| `businessweekly.py` | 商業周刊 | Native RSS |
| `cw.py` | 天下雜誌 | Google News RSS |
| `dramx.py` | DRAMX | Native RSS |
| `udn_money.py` | 經濟日報 | Google News RSS |
| `ctee.py` | 工商時報 | Google News RSS |
| `moneycontrol.py` | Moneycontrol | BeautifulSoup scraping |
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
| `sina_finance.py` | 新浪財經 | BeautifulSoup scraping |
| `einnews.py` | EIN News | BeautifulSoup scraping |
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
| `chosunbiz.py` | Chosun Biz | Playwright |

## Outputs

| File | Description |
|---|---|
| `news_crawler_latest.html` | Articles from the current crawler run |
| `today.html` | Articles from today + yesterday (filterable by source) |
| `important.html` | AI精選：⚡ past-12h top 30 + 📋 past-2d top 30, scored by Ollama |
| `grouped.html` | Cross-lingual same-event clusters (≥2 sources) |
| `analysis.json` | Machine-readable scored event list from the last analysis run |
| `data/recent.csv` | Git-tracked 7-day slice pushed to GitHub (feeds analyze_news.py) |
| `archive/YYYY-MM-DD.jsonl` | Full append-only local archive (git-ignored) |

## AI Analysis (`analyze_news.py`)

Reads `data/recent.csv`, clusters headlines by semantic similarity, then scores with local Ollama models. Runs independently of `run_crawlers.py`.

**Pipeline:**

1. **Stage 1 — Keyword filter**: hard-drop 股價 titles; remove obvious market noise (盤中/漲停/匯率/期貨…)
2. **Stage 2 — Embed + cluster**: `embeddinggemma:300m` vectors → cosine agglomerative clustering → cross-lingual same-event super-merge
3. **Stage 3 — Prescreen**: `qwen3:8b` tags each cluster as tech/non-tech + coarse score
4. **Stage 4 — Score + name**: `qwen3.6:35b-a3b` assigns a Traditional Chinese headline and a precise 0–100 importance score

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

```bash
python analyze_news.py
```

## Setup

```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
source venv/bin/activate

# Run all crawlers (writes news_crawler_latest.html + today.html)
python run_crawlers.py

# Run AI analysis (writes important.html + grouped.html + analysis.json)
python analyze_news.py

# Test a single crawler
python reuters.py
python zdkorea.py
# (any crawler module supports direct execution)
```

## Architecture

`run_crawlers.py` dynamically imports all crawler modules via `importlib`, runs them concurrently with `asyncio` + `ThreadPoolExecutor` (16 workers), deduplicates against the full JSONL archive, and writes HTML + CSV outputs.

Each crawler module exports a `fetch_<source>()` function returning `list[dict]` with keys: `domain`, `company`, `title`, `url`, `crawled_at`.

**ZDNet Korea** titles are auto-translated Korean → Traditional Chinese via Ollama (`qwen3:8b`) at crawl time. The stored title format is `韓文原標題（中文翻譯）`.
