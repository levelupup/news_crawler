import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_sheets(news_list):

    # 設定憑證與連線
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    key_path = os.path.join(os.environ['onedrive'], "automatic", "newscrawler-492407-35a654e26bba.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
    client = gspread.authorize(creds)
    # 定義所有要同步更新的試算表名稱
    
    target_sheets = ["News_history", "DIGITIMES Asia News History"]
    
    for sheet_name in target_sheets:
        try:
            sheet = client.open(sheet_name).sheet1
            # 取得現有連結以去重
            existing_urls = set(sheet.col_values(2)) 
            
            # 過濾出該表尚未存在的新聞
            new_rows = [
                [n['title'], n['url'], n['date'], n['description']]
                for n in news_list if n['url'] not in existing_urls
            ]
            
            # 執行插入
            if new_rows:
                # 建議先反轉，確保 list 中最新的一筆最後被 insert 到 row 2（即最頂端）
                new_rows.reverse() 
                sheet.insert_rows(new_rows, row=2)
                print(f"[{sheet_name}] 成功插入 {len(new_rows)} 則新聞")
            else:
                print(f"[{sheet_name}] 沒有新內容")
                
        except Exception as e:
            print(f"更新 {sheet_name} 時出錯: {e}")


# 假設這是從 Reuters API 撈出來的資料
mock_news = [
    {
        "title": "India Electronics Growth",
        "url": "https://www.reuters.com/tech-1",
        "date": "2026-04-05",
        "description": "Analysis of smartphone manufacturing in India."
    }
]
save_to_sheets(mock_news)
