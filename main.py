import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from fetchers.gdelt_fetcher import fetch_from_gdelt
from fetchers.newsapi_fetcher import fetch_from_newsapi


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def normalize_and_merge(news_items, gdelt_items):
    combined = news_items + gdelt_items
    df = pd.DataFrame(combined)
    df["published_at_parsed"] = pd.to_datetime(df["published_at"], errors="coerce")
    df = df.sort_values("published_at_parsed", ascending=False)
    df = df.drop_duplicates(subset="url", keep="first")
    return df.sort_values("published_at_parsed", ascending=False).reset_index(drop=True)


def main():

    query_filepath = "query_terms_short.json"

    with open(query_filepath, "r") as f:
        query_terms = json.load(f)

    output_dir = "weekly_archives"
    os.makedirs(output_dir, exist_ok=True)

    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=7)

    print(f"=== Fetching NewsAPI (from {from_date} to {to_date}) ===")
    all_news_items = []
    for chunk in chunk_list(query_terms, chunk_size=6):
        print(f">>> NewsAPI chunk: {chunk}")
        try:
            items = fetch_from_newsapi(
                query_terms=chunk, from_date=from_date, to_date=to_date, page_size=50
            )
            print(f"Retrieved {len(items)} items\n")
            all_news_items.extend(items)
        except Exception as e:
            print(f"NewsAPI chunk error: {e}\n")

    print(f"Total NewsAPI articles fetched: {len(all_news_items)}\n")

    print(f"=== Fetching GDELT (from {from_date} to {to_date}) ===")
    all_gdelt_items = []
    for chunk in chunk_list(query_terms, chunk_size=6):
        print(f">>> GDELT chunk: {chunk}")
        try:
            items = fetch_from_gdelt(
                query_terms=chunk, maxrecords=50, from_date=from_date, to_date=to_date
            )
            print(f"Retrieved {len(items)} items\n")
            all_gdelt_items.extend(items)
        except Exception as e:
            print(f"GDELT chunk error: {e}\n")

    print(f"Total GDELT articles fetched: {len(all_gdelt_items)}\n")

    df = normalize_and_merge(all_news_items, all_gdelt_items)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"weekly_combined_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=True)


if __name__ == "__main__":

    main()
