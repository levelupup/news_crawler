"""
鳳凰網科技 (tech.ifeng.com) news scraper.
"""
import requests
from lxml import etree

ROOT_URL = "https://tech.ifeng.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_ifeng(count: int = 20) -> list[dict]:
    """Return up to `count` articles from 鳳凰網科技."""
    response = requests.get(ROOT_URL, headers=HEADERS, timeout=15)
    response.encoding = "utf8"
    html = etree.HTML(response.text)

    seen = set()
    articles = []

    for node in html.xpath('//a[contains(@href,"tech.ifeng.com/c/")]'):
        href = node.attrib.get("href", "")
        if not href or href in seen:
            continue

        title = node.text_content().strip() if hasattr(node, "text_content") else (node.text or "")
        title = title.strip()
        if not title or len(title) < 5:
            continue

        # Skip items that look like category labels (very short, no Chinese chars)
        if len(title) < 6:
            continue

        seen.add(href)
        news_url = href if href.startswith("http") else ROOT_URL + href

        # Date is often in an adjacent element's text
        gp = node.getparent().getparent() if node.getparent() is not None else None
        published = ""
        if gp is not None:
            texts = [t.strip() for t in gp.itertext() if t.strip()]
            # Look for date-like token: "MM日" or "MM-DD"
            for t in texts:
                if ("日" in t and len(t) <= 5) or (len(t) == 5 and t[2] == "-"):
                    published = t
                    break

        articles.append({"title": title, "url": news_url, "published": published})
        if len(articles) >= count:
            break

    return articles


if __name__ == "__main__":
    articles = fetch_ifeng(count=20)
    print(f"Found {len(articles)} 鳳凰網科技 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
