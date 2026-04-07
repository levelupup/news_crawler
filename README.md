# News Crawler

Async news aggregator that crawls 19+ international tech/business sources and syncs results to Google Sheets.

## Sources

| Module | Display Name | Method |
|---|---|---|
| `bloomberg.py` | Bloomberg | Google News RSS |
| `reuters.py` | Reuters | Google News RSS |
| `wsj.py` | WSJ | Native RSS |
| `techcrunch.py` | TechCrunch | Native RSS |
| `theinformation.py` | The Information | Native RSS |
| `cnbc.py` | CNBC Technology | Native RSS |
| `scmp.py` | South China Morning Post | Native RSS |
| `thelec.py` | The Elec | Native RSS |
| `36kr.py` | 36kr.com | Google News RSS |
| `nikkei.py` | Nikkei Asia | Native RSS |
| `livemint.py` | Livemint | Native RSS |
| `economictimes.py` | Economic Times | Native RSS |
| `moneycontrol.py` | Moneycontrol | BeautifulSoup scraping |
| `chinaflashmarket.py` | 中國閃存市場 | BeautifulSoup scraping |
| `chinastarmarket.py` | — | BeautifulSoup scraping |
| `c114.py` | C114通信網 | BeautifulSoup scraping |
| `ifeng.py` | 鳳凰網科技 | BeautifulSoup scraping |
| `sina_finance.py` | 新浪財經 | BeautifulSoup scraping |
| `sohu.py` | 搜狐IT | Playwright + stealth |
| `einnews.py` | EIN News | BeautifulSoup scraping |

## Outputs

| File | Description |
|---|---|
| `news_crawler_latest.html` | Articles from the current run |
| `today.html` | Articles from today + yesterday |
| `data/*.csv` | Per-domain history (rolling 90 days) |

The two HTML pages have a fixed button in the top-right corner to switch between them.

## Setup

```bash
pip install requests beautifulsoup4 feedparser \
            googlenewsdecoder playwright playwright_stealth lxml pandas
playwright install chromium
```

## Usage

```bash
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
