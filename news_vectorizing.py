import os
import pandas as pd
from openai import OpenAI
from sklearn.decomposition import PCA
import hdbscan


api_key = os.environ["OpenAI_API_KEY"]
client = OpenAI(api_key=api_key)

tables = pd.read_html('today.html')
if not tables:
    raise ValueError("today.html 中找不到表格")
df = tables[0]
if 'Title' not in df.columns:
    raise ValueError(f"找不到 Title 欄位，現有欄位：{df.columns.tolist()}")

titles = df['Title'].tolist()

response = client.embeddings.create(
    input=titles,
    model="text-embedding-3-small"
)
embeddings = [item.embedding for item in response.data]

n_components = min(50, len(titles))
X = PCA(n_components=n_components).fit_transform(embeddings)

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=5,
    metric='euclidean'
)

labels = clusterer.fit_predict(X)

df['cluster'] = labels
df.to_csv('today_clustered.csv', index=False, encoding='utf-8-sig')
print(f"共 {len(titles)} 篇，分成 {labels.max() + 1} 個群組（-1 為雜訊），結果存至 today_clustered.csv")