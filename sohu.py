"""
搜狐IT (it.sohu.com) news scraper.

it.sohu.com renders content via JavaScript, so Playwright is required.
"""
import asyncio
import re
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def _fetch(count: int) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        stealth = Stealth()
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        await stealth.apply_stealth_async(page)
        await page.goto("https://it.sohu.com", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)

        seen = set()
        articles = []

        for node in await page.query_selector_all('a[href*="sohu.com/a/"]'):
            href = await node.get_attribute("href")
            if not href or href in seen:
                continue

            title = (await node.inner_text()).strip()
            if not title or len(title) < 5:
                continue

            # Strip tracking query params; keep clean URL
            clean_url = href.split("?")[0]
            seen.add(href)

            articles.append({"title": title, "url": clean_url, "published": ""})
            if len(articles) >= count:
                break

        await browser.close()
        return articles


def fetch_sohu(count: int = 20) -> list[dict]:
    """Return up to `count` articles from 搜狐IT."""
    return asyncio.run(_fetch(count))


if __name__ == "__main__":
    articles = fetch_sohu(count=20)
    print(f"Found {len(articles)} 搜狐IT articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
