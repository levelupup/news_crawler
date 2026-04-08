"""
The Edge Markets (theedgemarkets.com) tech news scraper.
"""
import html as html_module
import requests
from bs4 import BeautifulSoup

ROOT_URL = 'https://www.theedgemarkets.com/'


def fix_title(t):
    if t is None:
        return t
    try:
        t = t.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return html_module.unescape(t)


def fetch_edge_markets(count: int = 20) -> list[dict]:
    """Return up to `count` tech articles from The Edge Markets."""
    response = requests.get(f'{ROOT_URL}flash-categories/tech', timeout=15)
    soup = BeautifulSoup(response.text, 'lxml')
    elements = soup.find_all('div', {'class': 'views-field views-field-field-image'})
    result = []
    for e in elements[:count]:
        children = e.findChildren('a')
        img_children = e.findChildren('img')
        if not children or not img_children:
            continue
        result.append({
            'title': fix_title(img_children[0].get('alt', '')),
            'url': ROOT_URL + children[0].get('href', ''),
            'published': '',
        })
    return result


if __name__ == '__main__':
    articles = fetch_edge_markets(count=20)
    print(f"Found {len(articles)} Edge Markets articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
