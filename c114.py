"""
C114通信網 (c114.com.cn) news scraper.
"""
import requests
from lxml import etree

ROOT_URL = "http://www.c114.com.cn"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_c114(count: int = 20) -> list[dict]:
    """Return up to `count` articles from C114通信網."""
    url = f"{ROOT_URL}/news/"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.encoding = "gbk"
    html = etree.HTML(response.text)

    articles = []
    for node in html.xpath('//div[@class="new_list_c"]/h6/a'):
        title = node.text_content().strip() if hasattr(node, "text_content") else (node.text or "")
        href = node.attrib.get("href", "")
        if not title or not href:
            continue

        news_url = href if href.startswith("http") else ROOT_URL + href
        articles.append({"title": title, "url": news_url, "published": ""})
        if len(articles) >= count:
            break

    return articles


if __name__ == "__main__":
    articles = fetch_c114(count=20)
    print(f"Found {len(articles)} C114通信網 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
