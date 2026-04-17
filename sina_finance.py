import requests, os
from datetime import datetime
import collections
import pandas as pd
import re
import webbrowser
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# Define the URLs for different companies
urls = {
    "立訊":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002475.phtml",
    "歌爾":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002241.phtml",
    "聞泰":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600745.phtml",
    "環旭電子":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh601231.phtml",
    "華勤技術":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603296.phtml",
    "冠捷科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz000727.phtml",
    "藍思":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300433.phtml",
    "摩爾線程":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688795.phtml",
    "晶合集成":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688249.phtml",
    "中芯國際":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688981.phtml",
    "通富微電":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002156.phtml",
    "長電科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600584.phtml",
    "華天科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002185.phtml",
    "格科微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688728.phtml",
    "韋爾股份":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603501.phtml",
    "豪威集團":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600460.phtml",
    "華潤微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688396.phtml",
    "華微電子":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600360.phtml",
    "國民技術":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300077.phtml",
    "兆易創新":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603986.phtml",
    "瀾起科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688008.phtml",
    "北方華創":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002371.phtml",
    "晶盛機電":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300316.phtml",
    "中微半導體":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688012.phtml",
    "至純科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh6039690.phtml",
    "盛美上海":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688082.phtml",
    "拓荊科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688072.phtml",
    "華海清科":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688120.phtml",
    "芯源微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688037.phtml",
    "納芯微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688052.phtml",
    "景嘉微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300474.phtml",
    "海光信息":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688041.phtml",
    "太極實業":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600667.phtml",
    "深科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz000021.phtml",
    "華大九天":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz301269.phtml",
    "中科飛測":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688361.phtml",
    "滬矽產業":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688126.phtml",
    "概倫電子":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688206.phtml",
    "長川科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300604.phtml",
    "南大光電":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300346.phtml",
    "安集科技":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688019.phtml",
    "華峰測控":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688200.phtml",
    "國軒高科":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002074.phtml",
    "寧德時代":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300750.phtml",
    "比亞迪":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz002594.phtml",
    "億緯鋰能":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz300014.phtml",
    "華虹":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh688347.phtml",
    "士蘭微":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600460.phtml",
    "中科曙光":"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh603019.phtml",
}

# File paths
dest = os.getenv('onedrive') + '/automatic/regional_news_for_chinese_ems.csv'
html = os.getenv('onedrive') + '/automatic/regional_update_chinese_ems.html'
now = datetime.now().strftime('%Y-%m-%d %H:%M')

# Regex patterns
pat = r'(\d{4}-\d{2}-\d{2} \d{2}\:\d{2}.*?</a>)'
pat1 = '\d{4}-\d{2}-\d{2} \d{2}\:\d{2}'
pat2 = r'(http.*?)\'>'  
pat3 = '>(.*?)<'

news_items = []

for k, v in urls.items():

    response = session.get(v, timeout=10)

    original_text = re.findall(r'datelist"><ul>(.*?)</ul>', response.text, re.S|re.M)[0]
    original_text = original_text.replace('&nbsp;', ' ').strip()

    results = re.findall(pat, original_text, re.S|re.M)

    for result in results:
        try:
            company = k
            date = re.findall(pat1, result, re.S|re.M)[0]
            link = re.findall(pat2, result, re.S|re.M)[0]
            title = re.findall(pat3, result, re.S|re.M)[0]

            news_items.append([company, date, link, title, now])

        except:
            print(result)


# Update dataframe
df_update = pd.DataFrame(news_items, columns=['company','date','href','title','retrieved'])
df_update = df_update.set_index('href')

dict_update = {row[0]:[row[1],row[2],row[3]] for row in df_update.itertuples()}

# Load history
if os.path.exists(dest):

    df_history = pd.read_csv(dest, encoding='utf-8-sig')
    df_history = df_history.set_index('href')

else:

    df_history = pd.DataFrame(columns=['company','date','href','title','retrieved'])
    df_history = df_history.set_index('href')

dict_history = {row[0]:[row[1],row[2],row[3]] for row in df_history.itertuples()}

# Compare
updated = {k:dict_update[k] for k in set(dict_update)-set(dict_history)}
updated = {v[0]:[k,v[1],v[2]] for k,v in updated.items()}
updated = collections.OrderedDict(sorted(updated.items()))

# Merge
df_total = pd.concat([df_update,df_history],axis=0)
df_total = df_total[~df_total.index.duplicated(keep='first')]
df_total = df_total.sort_values(by=['retrieved','href','title'])

df_total.to_csv(dest, encoding='utf-8-sig')

# Write HTML
with open(html,'w',encoding='utf8') as f:

    text = '''
    <head>
        <style>
        body {font-family: Arial;background:#f4f4f9;}
        table {width:100%;border-collapse:collapse;}
        th,td {padding:10px;border-bottom:1px solid #ddd;}
        th {background:#f1f1f1;}
        a {color:#007bff;text-decoration:none;}
        </style>
    </head>
    <body>
    <h1>Recent News Updates for Chinese EMS and Semiconductor Companies</h1>
    <table>
    <tr><th>Company</th><th>Title</th></tr>
    '''

    for k,v in updated.items():

        text += f'''
        <tr>
        <td>{k}</td>
        <td><a href="{v[0]}" target="_blank">{v[2]}</a></td>
        </tr>
        '''

    text += '''
    </table>
    </body>
    '''

    f.write(text)

webbrowser.open(html,new=2)
