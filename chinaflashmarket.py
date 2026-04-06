"""
中國閃存市場 (chinaflashmarket.com) news scraper.
"""
import requests
from lxml import etree

ROOT_URL = "https://www.chinaflashmarket.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_chinaflashmarket(count: int = 20) -> list[dict]:
    """Return up to `count` articles from 中國閃存市場."""
    url = f"{ROOT_URL}/news/"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.encoding = "utf8"
    html = etree.HTML(response.text)

    articles = []
    # News items are h3/a elements NOT inside a carousel
    for el in html.xpath("//h3/a[not(ancestor::*[contains(@class,'carousel')])]"):
        title = el.text_content().strip() if hasattr(el, "text_content") else (el.text or "")
        href = el.attrib.get("href", "")
        if not title or not href:
            continue

        news_url = ROOT_URL + href if href.startswith("/") else href

        # Date is the last text node in the grandparent container
        gp = el.getparent().getparent()
        texts = [t.strip() for t in gp.itertext() if t.strip()]
        # Last token that looks like a date (YYYY-MM-DD)
        published = next((t for t in reversed(texts) if len(t) == 10 and t[4] == "-"), "")

        articles.append({"title": title, "url": news_url, "published": published})
        if len(articles) >= count:
            break

    return articles


if __name__ == "__main__":
    articles = fetch_chinaflashmarket(count=20)
    print(f"Found {len(articles)} 中國閃存市場 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
