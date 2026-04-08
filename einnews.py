import os, webbrowser, pandas as pd, collections
import requests, re, html as html_module
from bs4 import BeautifulSoup
from datetime import datetime

def fix_title(t):
    if t is None:
        return t
    try:
        t = t.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return html_module.unescape(t)

# countries = ['malaysia','india','indonesia','vietnam','philippines','thailand','singapore']
countries = ['india']
domains = ['electriccars','semiconductors','cellphones','tech','solarenergy','electronics']
dest = os.getenv('onedrive') + '/automatic/regional_news.xlsx'
html = os.getenv('onedrive') + '/automatic/regional_update.html'
now = datetime.now().strftime('%Y-%m-%d %H:%M')
all_titles, all_hrefs, media, retrieved = [],[],[],[]

def einnews():
    for dm in domains:
        urls = [f'https://{dm}.einnews.com/country/{ctry}' for ctry in countries]
        root_url = f'https://{dm}.einnews.com'
        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text,'lxml')
            h3s = soup.find_all('a',{"class":"title"})
            hrefs = [h.get('href') for h in h3s]
            titles = [fix_title(h.text) for h in h3s]
            adjusted_href = []
            for href in hrefs:
                href = href[:href.find('?')] if '?' in href else href
                href = f'{root_url}{href}' if not 'https://' in href else href
                adjusted_href.append(href)
            [all_titles.append(h) for h in titles]
            [all_hrefs.append(h) for h in adjusted_href]
            [media.append('einnews') for h in hrefs]
            [retrieved.append(now) for h in hrefs]

commands = [einnews()]

for command in commands:
    try:
        command
    except:
        pass
    

#df_update：這次掃到（DataFrame）
#dict_update：這次掃到（字典格式）
#df_history：過去掃到（DataFrame）
#dict_history：過去掃到（字典格式）    

df_update = pd.DataFrame({'href':all_hrefs,'title':all_titles,'media':media,'retrieved':retrieved})
df_update = df_update.set_index('href')
dict_update = {row[0]:[row[1],row[2],row[3]] for row in df_update.itertuples()}
df_history = pd.read_excel(dest,engine='openpyxl')
df_history = df_history.set_index('href')
dict_history = {row[0]:[row[1],row[2],row[3]] for row in df_history.itertuples()}


#updated：這次掃到-過去掃到 = 本次新增
#比對舊資料、去除標題及連結重複後依來源排序
updated = {k:dict_update[k] for k in set(dict_update) - set(dict_history)}
updated = {v[0]:[k,v[1],v[2]] for k,v in updated.items()}
updated = {v[0]:[k,v[1],v[2]] for k,v in updated.items()}
updated = collections.OrderedDict(sorted(updated.items()))

df_total = pd.concat([df_update,df_history],axis=0)
df_total = df_total[~df_total.index.duplicated(keep='first')]
df_total = df_total.sort_values(by=['retrieved','media','title'])
df_total.to_excel(dest)

# Write the results to an HTML file with improved styling
with open(html, 'w', encoding='utf8') as f:
    text = '''
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 80%;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            table {
                width: 100%;
                margin: 20px 0;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f1f1f1;
            }
            tr:hover {
                background-color: #f9f9f9;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Recent Indian News Updates</h1>
            <table>
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Title</th>
                    </tr>
                </thead>
                <tbody>
    '''
    for k, v in updated.items():
        text += f'''
            <tr>
                <td>{v[1]}</td>
                <td><a href="{k}" target="_blank">{v[0]}</a></td>
            </tr>
        '''
    text += '''
                </tbody>
            </table>
        </div>
    </body>
    '''
    f.write(text)

# Open the HTML file in the browser
webbrowser.open(html, new=2)
