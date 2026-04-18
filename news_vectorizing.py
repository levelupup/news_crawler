import os
import json
import time
import pandas as pd
from openai import OpenAI
from typing import Optional


def load_articles(html_path: str = "today.html") -> pd.DataFrame:
    tables = pd.read_html(html_path)
    if not tables:
        raise ValueError(f"{html_path} 中找不到表格")
    df = tables[0]
    if "Title" not in df.columns:
        raise ValueError(f"找不到 Title 欄位，現有欄位：{df.columns.tolist()}")
    return df


def build_prompt(titles: list[str]) -> str:
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    n = len(titles)
    return f"""You are a financial and tech news classifier. Given a list of {n} news article titles (numbered), extract structured metadata for each one.

Return a JSON object with a single key "items" containing an array of exactly {n} objects in the same order. Each object must have these fields:

- "company": string or null — the primary company name mentioned (use canonical English name, e.g. "TSMC" not "台積電"). null if no specific company.
- "country": string or null — the company's home country as a 2-letter ISO code (TW, US, JP, CN, KR, IN, etc.). null if unknown or no company.
- "industry": string or null — one of: semiconductor, software, ev, finance, telecom, media, energy, retail, auto, biotech, hardware, other. null if no company.
- "event_type": one of exactly: earnings, product_launch, stock_movement, topic, general
  - earnings: financial results, 財報, 季報, revenue/profit announcements
  - product_launch: new product, new model, new service announcement by a specific company
  - stock_movement: pure price movement (漲/跌/收盤/盤中/股價) with no substantive news reason
  - topic: thematic macro topic crossing multiple companies/countries (trade war, AI unemployment, geopolitics)
  - general: everything else
- "topic_label": string or null — ONLY when event_type is "topic": a short 2-8 character Chinese or English label (e.g. "AI失業衝擊", "關稅貿易戰"). null for all other event types.

Titles:
{numbered}

Return only the JSON object with the "items" array, no extra text."""


def extract_metadata_batch(
    client: OpenAI,
    titles: list[str],
    batch_size: int = 30,
    model: str = "gpt-4.1-mini",
    retry_limit: int = 3,
) -> list[dict]:
    results = []
    total = len(titles)

    for start in range(0, total, batch_size):
        batch = titles[start:start + batch_size]
        print(f"  處理 {start+1}–{min(start+len(batch), total)} / {total}...")

        success = False
        for attempt in range(retry_limit):
            try:
                response = client.chat.completions.create(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You return only valid JSON."},
                        {"role": "user", "content": build_prompt(batch)},
                    ],
                    temperature=0,
                )
                parsed = json.loads(response.choices[0].message.content)
                items = parsed.get("items", parsed) if isinstance(parsed, dict) else parsed
                if isinstance(items, list) and len(items) == len(batch):
                    results.extend(items)
                    success = True
                    break
            except Exception as e:
                print(f"    第 {attempt+1} 次失敗：{e}")
            time.sleep(2 ** (attempt + 1))

        if not success:
            print(f"    批次 {start}–{start+len(batch)} 全部重試失敗，使用預設值")
            results.extend(
                {"company": None, "country": None, "industry": None,
                 "event_type": "general", "topic_label": None}
                for _ in batch
            )

    return results


def assign_cluster_label(row: pd.Series) -> Optional[str]:
    et = row.get("event_type", "general")

    if et == "stock_movement":
        return None

    if et == "earnings":
        company = row.get("company")
        return f"財報-{company}" if company else "財報"

    if et == "product_launch":
        company = row.get("company")
        return f"新品-{company}" if company else "新品"

    if et == "topic":
        label = row.get("topic_label")
        return label if label else "topic-unknown"

    company = row.get("company")
    country = row.get("country") or "XX"
    industry = row.get("industry") or "other"

    if company:
        return f"{country}-{industry}-{company}"
    return f"{country}-{industry}"


def run_pipeline(html_path: str = "today.html", output_path: str = "today_clustered.csv") -> None:
    df = load_articles(html_path)
    titles = df["Title"].tolist()
    print(f"載入 {len(titles)} 篇文章")

    api_key = os.environ["OpenAI_API_KEY"]
    client = OpenAI(api_key=api_key)

    print("Stage 1：LLM 結構化抽取...")
    metadata = extract_metadata_batch(client, titles)

    meta_df = pd.DataFrame(metadata)[["company", "country", "industry", "event_type", "topic_label"]]
    df = pd.concat([df.reset_index(drop=True), meta_df], axis=1)

    print("Stage 2：規則分組...")
    df["cluster_label"] = df.apply(assign_cluster_label, axis=1)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    excluded = df["cluster_label"].isna().sum()
    unique_clusters = df["cluster_label"].dropna().nunique()
    print(f"完成。{len(titles)} 篇 → {unique_clusters} 個群組，{excluded} 篇純股價報導不分類")
    print(f"輸出：{output_path}")


if __name__ == "__main__":
    run_pipeline()
