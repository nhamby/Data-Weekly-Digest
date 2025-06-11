import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from email_creation import send_news_email, RECIPIENT_EMAIL
from fetchers.gdelt_fetcher import fetch_from_gdelt
from fetchers.newsapi_fetcher import fetch_from_newsapi
from semantic_similarity import get_relevant_articles
from summarize_gemini import summarize_article_gemini


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

    output_dir_weekly_archives = "weekly_archives"
    os.makedirs(output_dir_weekly_archives, exist_ok=True)

    output_dir_top_articles = "top_articles"
    os.makedirs(output_dir_top_articles, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    # to_date = datetime.now(timezone.utc).date()
    # from_date = to_date - timedelta(days=7)

    # print(f"=== Fetching NewsAPI (from {from_date} to {to_date}) ===")
    # all_news_items = []
    # for chunk in chunk_list(query_terms, chunk_size=6):
    #     print(f">>> NewsAPI chunk: {chunk}")
    #     try:
    #         items = fetch_from_newsapi(
    #             query_terms=chunk, from_date=from_date, to_date=to_date, page_size=50
    #         )
    #         print(f"Retrieved {len(items)} items\n")
    #         all_news_items.extend(items)
    #     except Exception as e:
    #         print(f"NewsAPI chunk error: {e}\n")

    # print(f"Total NewsAPI articles fetched: {len(all_news_items)}\n")

    # print(f"=== Fetching GDELT (from {from_date} to {to_date}) ===")
    # all_gdelt_items = []
    # for chunk in chunk_list(query_terms, chunk_size=6):
    #     print(f">>> GDELT chunk: {chunk}")
    #     try:
    #         items = fetch_from_gdelt(
    #             query_terms=chunk, maxrecords=50, from_date=from_date, to_date=to_date
    #         )
    #         print(f"Retrieved {len(items)} items\n")
    #         all_gdelt_items.extend(items)
    #     except Exception as e:
    #         print(f"GDELT chunk error: {e}\n")

    # print(f"Total GDELT articles fetched: {len(all_gdelt_items)}\n")

    # df = normalize_and_merge(all_news_items, all_gdelt_items)

    # filename = f"weekly_combined_{timestamp}.csv"
    # output_path = os.path.join(output_dir_weekly_archives, filename)
    # df.to_csv(output_path, index=True)

    # loaded_df = pd.read_csv(
    #     "weekly_archives/weekly_combined_2025-06-11.csv"
    # )  # .head(139)

    # query = "data procurement and data acquisition"

    # top_articles = get_relevant_articles(loaded_df, query, 10)

    # print(f"\n=== Summarizing Top Articles ===")

    # top_articles["summary"] = top_articles.apply(
    #     lambda row: summarize_article_gemini(
    #         source=row["source"],
    #         title=row["title"],
    #         url=row["url"],
    #         published_at=row["published_at"],
    #         description=row["description"],
    #         content=row["content"],
    #     ),
    #     axis=1,
    # )

    # filename = f"top_articles_{timestamp}.csv"
    # output_path = os.path.join(output_dir_top_articles, filename)
    # top_articles.to_csv(output_path, index=True)

    # print(f"===         Completed        ===\n")

    loaded_top_df = pd.read_csv("top_articles/top_articles_2025-06-11.csv")

    recipient_email = RECIPIENT_EMAIL

    print(f"=== Sending Email to {recipient_email} ===")
    send_news_email(loaded_top_df, recipient_email)
    print(f"===   Sent Email to {recipient_email}  ===")


if __name__ == "__main__":

    main()
