# News Crawler

Async news aggregator that crawls 55+ international tech/business sources and syncs results to Google Sheets.

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
| `zdkorea.py` | ZDNet Korea | Native RSS |
| `36kr.py` | 36kr.com | Google News RSS |
| `nikkei.py` | Nikkei Asia | Native RSS |
| `nytimes.py` | NYT中文網 | Native RSS |
| `livemint.py` | Livemint | Native RSS |
| `economictimes.py` | Economic Times | Native RSS |
| `9to5mac.py` | 9to5Mac | Native RSS |
| `appleinsider.py` | AppleInsider | Native RSS |
| `electrek.py` | Electrek | Native RSS |
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
| `laoyaoba.py` | 集微網 | Native RSS |
| `ofweek.py` | OFweek (11 verticals) | BeautifulSoup scraping |
|   | - 機器人網 (Robot) |  |
|   | - 人工智能網 (AI) |  |
|   | - 智能製造網 (Smart Manufacturing) |  |
|   | - 顯示網 (Display) |  |
|   | - 雲計算網 (Cloud Computing) |  |
|   | - 鋰電網 (Lithium Battery) |  |
|   | - 傳感器網 (Sensor) |  |
|   | - 新能源汽車網 (New Energy Vehicles) |  |
|   | - 儲能網 (Energy Storage) |  |
|   | - 智能硬件網 (Smart Hardware) |  |
|   | - 光通訊網 (Optical Communications) |  |
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
| `icviews.py` | 半導縱橫 | JSON API (messagePool) |
| `sohu.py` | 搜狐IT | Playwright + stealth |
| `sohu_xinzhixun.py` | 芯智訊 (搜狐號) | Playwright + stealth |

## Outputs

| File | Description |
|---|---|
| `news_crawler_latest.html` | Articles from the current run |
| `today.html` | Articles from today + yesterday |
| `data/*.csv` | Per-domain history (rolling 90 days) |

The two HTML pages have a fixed button in the top-right corner to switch between them.

## Setup

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
# Activate venv first (if not already active)
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Run all crawlers
python run_crawlers.py

# Test a single crawler
python reuters.py
python sohu.py
# (any crawler module supports direct execution)
```

## Architecture

`run_crawlers.py` dynamically imports all crawler modules via `importlib`, runs them concurrently with `asyncio` + `ThreadPoolExecutor` (16 workers), deduplicates against `data/*.csv` history, and writes HTML outputs.

Each crawler module exports a `fetch_<source>()` function returning `list[dict]` with keys: `domain`, `company`, `title`, `url`, `crawled_at`.
