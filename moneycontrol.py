"""
Moneycontrol news scraper.

Fetches articles by parsing the article listing pages for Economy and Companies sections.
No date is available in the listing HTML; published is left empty.
"""
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

PAGES = {
    "economy":   "https://www.moneycontrol.com/news/business/economy/",
    "companies": "https://www.moneycontrol.com/news/business/companies/",
}


def _fetch_page(url: str, count: int) -> list[dict]:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    ul = soup.find("ul", id="cagetory")
    if not ul:
        return []
    articles = []
    for li in ul.find_all("li", class_="clearfix")[:count]:
        a = li.find("a", href=True)
        h2 = li.find("h2")
        if a and h2:
            articles.append({
                "title":     h2.get_text(strip=True),
                "url":       a["href"],
                "published": "",
            })
    return articles


def fetch_moneycontrol_economy(count: int = 20) -> list[dict]:
    """Return up to `count` Moneycontrol Economy articles."""
    return _fetch_page(PAGES["economy"], count)


def fetch_moneycontrol_companies(count: int = 20) -> list[dict]:
    """Return up to `count` Moneycontrol Companies articles."""
    return _fetch_page(PAGES["companies"], count)


def fetch_moneycontrol(count: int = 20) -> list[dict]:
    """Return up to `count` Moneycontrol articles across all sections (deduplicated)."""
    seen = set()
    articles = []
    for key in PAGES:
        for a in _fetch_page(PAGES[key], count):
            if a["url"] not in seen:
                seen.add(a["url"])
                articles.append(a)
            if len(articles) >= count:
                return articles
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    for name, fn in [
        ("Economy",   fetch_moneycontrol_economy),
        ("Companies", fetch_moneycontrol_companies),
    ]:
        articles = fn(count=5)
        print(f"=== Moneycontrol {name} ({len(articles)} articles) ===")
        for i, a in enumerate(articles, 1):
            print(f"{i:3}. {a['title']}")
            print(f"     {a['url']}")
        print()
