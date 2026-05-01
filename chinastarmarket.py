"""
科創板日報 (chinastarmarket.cn) news scraper.
"""
import json
import requests
from lxml import etree

ROOT_URL = "https://www.chinastarmarket.cn"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_chinastarmarket(count: int = 20) -> list[dict]:
    """Return up to `count` articles from 科創板日報."""
    response = requests.get(ROOT_URL, headers=HEADERS, timeout=15)
    response.encoding = "utf8"
    html = etree.HTML(response.text)

    nd = html.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not nd:
        return []

    data = json.loads(nd[0])
    page_data = data.get("props", {}).get("pageProps", {}).get("data", {})

    # top_article and depth_list contain the real article IDs used in /detail/<id> URLs
    raw = page_data.get("top_article", []) + page_data.get("depth_list", [])

    articles = []
    seen = set()
    for item in raw:
        article_id = item.get("id")
        title = item.get("title", "")
        if not article_id or not title or article_id in seen:
            continue
        seen.add(article_id)
        articles.append({
            "title": title,
            "url": f"{ROOT_URL}/detail/{article_id}",
            "published": "",
        })
        if len(articles) >= count:
            break

    return articles


if __name__ == "__main__":
    articles = fetch_chinastarmarket(count=20)
    print(f"Found {len(articles)} 科創板日報 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
