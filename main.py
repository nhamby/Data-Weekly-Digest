import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from email_creation import send_news_email, RECIPIENT_EMAIL
from fetchers.gdelt_fetcher import fetch_all_from_gdelt
from fetchers.newsapi_fetcher import fetch_all_from_newsapi
from helper_functions import normalize_and_merge
from semantic_similarity import filter_articles, get_relevant_articles
from summarize_gemini import summarize_article_gemini


def main():

    query_filepath = "query_terms_short.json"

    with open(query_filepath, "r") as f:
        query_terms = json.load(f)

    output_dir_weekly_archives = "weekly_archives"
    os.makedirs(output_dir_weekly_archives, exist_ok=True)

    output_dir_top_articles = "top_articles"
    os.makedirs(output_dir_top_articles, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=7)

    all_newsapi_items = fetch_all_from_newsapi(
        query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
    )

    all_gdelt_items = fetch_all_from_gdelt(
        query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
    )

    df = normalize_and_merge(all_newsapi_items, all_gdelt_items)

    filename = f"weekly_combined_{timestamp}.csv"
    output_path = os.path.join(output_dir_weekly_archives, filename)
    df.to_csv(output_path, index=True)

    loaded_df_filename = f"weekly_archives/weekly_combined_{timestamp}.csv"
    loaded_df = pd.read_csv(loaded_df_filename)

    query = "data procurement and data acquisition"

    top_articles = get_relevant_articles(loaded_df, query, 10)

    top_articles_filtered = filter_articles(top_articles)
    
    print(f"\nSummarizing Top Articles...\n")

    top_articles_filtered["summary"] = top_articles_filtered.apply(
        lambda row: summarize_article_gemini(
            source=row["source"],
            title=row["title"],
            url=row["url"],
            published_at=row["published_at"],
            description=row["description"],
            content=row["content"],
        ),
        axis=1,
    )

    filename = f"top_articles_{timestamp}.csv"
    output_path = os.path.join(output_dir_top_articles, filename)
    top_articles_filtered.to_csv(output_path, index=True)

    loaded_top_df_filename = f"top_articles/top_articles_{timestamp}.csv"
    loaded_top_df = pd.read_csv(loaded_top_df_filename)

    send_news_email(loaded_top_df, RECIPIENT_EMAIL)
    print(f"Email sent successfully to {RECIPIENT_EMAIL}!\n")


if __name__ == "__main__":

    main()
