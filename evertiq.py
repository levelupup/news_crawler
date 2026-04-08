"""
Evertiq (evertiq.com) Asia-Pacific news scraper.
"""
import html as html_module
import requests
from bs4 import BeautifulSoup

ROOT_URL = 'https://evertiq.com'


def fix_title(t):
    if t is None:
        return t
    try:
        t = t.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return html_module.unescape(t)


def fetch_evertiq(count: int = 20) -> list[dict]:
    """Return up to `count` Asia-Pacific articles from Evertiq."""
    response = requests.get(f'{ROOT_URL}/region/Asia-Pacific', timeout=15)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('span', {'class': 'header'})
    result = []
    for h in articles[:count]:
        result.append({
            'title': fix_title(h.string.strip()) if h.string else '',
            'url': f"{ROOT_URL}{h.parent.get('href', '')}",
            'published': '',
        })
    return result


if __name__ == '__main__':
    articles = fetch_evertiq(count=20)
    print(f"Found {len(articles)} Evertiq articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
