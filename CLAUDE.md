# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Async news crawler that aggregates tech/business news from 16+ international sources (Chinese, Indian, Western) and syncs results to Google Sheets. The main entry point is `run_crawlers.py`.

## Running

```bash
# Run all crawlers
python run_crawlers.py

# Test a single crawler
python reuters.py
python nikkei.py
python sohu.py
# (any crawler module supports direct execution)
```

## Architecture

**Orchestration (`run_crawlers.py`):**
- Dynamically imports all crawler modules via `importlib`
- Runs them concurrently via `asyncio` + `ThreadPoolExecutor` (16 workers)
- Deduplicates against historical URLs stored in `data/*.csv` (one CSV per domain)
- Generates three HTML outputs: `news_crawler_latest.html`, `today.html`, `news_history_all.html`
- Syncs to Google Sheets ("News Crawler" spreadsheet, worksheets: Latest / Today / History)

**Each crawler module** exports a `fetch_<source>()` function returning `list[dict]` with keys: `domain`, `company`, `title`, `url`, `crawled_at`.

**Four crawler implementation patterns:**
1. **Google News RSS + `googlenewsdecoder`** — used for bot-protected sites (Bloomberg, Reuters, WSJ, TechCrunch, 36kr, etc.)
2. **Native RSS feeds** — direct feedparser parsing (Livemint, Economic Times)
3. **BeautifulSoup/lxml HTML scraping** — static pages (Moneycontrol, chinaflashmarket, c114, ifeng)
4. **Playwright + stealth (async)** — JS-rendered pages (Sohu IT)

## Environment / Credentials

Google Sheets auth uses a service account JSON file. Path is constructed as:
```python
os.environ["onedrive"] + "/automatic/newscrawler-492407-e08b0b8abcf7.json"
```
The `onedrive` environment variable must point to the OneDrive root directory.

## Key Dependencies

`gspread`, `oauth2client`, `requests`, `beautifulsoup4`, `feedparser`, `googlenewsdecoder`, `playwright`, `playwright_stealth`, `lxml`, `pandas`

Install Playwright browsers: `playwright install chromium`
