"""
Silicon Semiconductor China (siscmag.com) news scraper.
"""
import html as html_module
import requests
from bs4 import BeautifulSoup

ROOT_URL = 'https://www.siscmag.com'


def fix_title(t):
    if t is None:
        return t
    try:
        t = t.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return html_module.unescape(t)


def fetch_silicon_semiconductor_china(count: int = 20) -> list[dict]:
    """Return up to `count` articles from Silicon Semiconductor China."""
    response = requests.get(f'{ROOT_URL}/news/3-1.html', timeout=15)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('article', {'class': 'block_topic_post'})
    result = []
    for article in articles[:count]:
        a = article.p.a if article.p else None
        if not a:
            continue
        result.append({
            'title': fix_title(a.text.strip()),
            'url': ROOT_URL + a['href'],
            'published': '',
        })
    return result


if __name__ == '__main__':
    articles = fetch_silicon_semiconductor_china(count=20)
    print(f"Found {len(articles)} Silicon Semiconductor China articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
