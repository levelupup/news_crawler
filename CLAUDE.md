# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Async news crawler that aggregates tech/business news from international sources. The main entry point is `run_crawlers.py`.

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
- Runs them concurrently via `asyncio` + `ThreadPoolExecutor`
- Deduplicates against historical URLs stored in `data/*.csv` (one CSV per domain)
- Generates two HTML outputs: `news_crawler_latest.html`, `today.html`

**Each crawler module** exports a `fetch_<source>()` function returning `list[dict]` with keys: `domain`, `company`, `title`, `url`, `crawled_at`.

**Four crawler implementation patterns:**
1. **Google News RSS + `googlenewsdecoder`** — used for bot-protected sites (Bloomberg, Reuters, 36kr, etc.)
2. **Native RSS feeds** — direct feedparser parsing (Livemint, Economic Times)
3. **BeautifulSoup/lxml HTML scraping** — static pages (Moneycontrol, chinaflashmarket, c114, ifeng)
4. **Playwright + stealth (async)** — JS-rendered pages (Sohu IT)

## Key Dependencies

`requests`, `beautifulsoup4`, `feedparser`, `googlenewsdecoder`, `playwright`, `playwright_stealth`, `lxml`, `pandas`

Install Playwright browsers: `playwright install chromium`
