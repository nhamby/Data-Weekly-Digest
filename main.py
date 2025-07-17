import json
import os
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from html_and_email_functions import (
    export_standalone_html,
    send_news_email,
    RECIPIENT_EMAIL,
)
from fetchers.gdelt_fetcher import fetch_all_from_gdelt
from fetchers.newsapi_fetcher import fetch_all_from_newsapi
from helper_functions import normalize_and_merge
from semantic_similarity import filter_articles, get_relevant_articles
from summarize_articles import summarize_article_gemini


def main():

    query_terms_length = "short"
    query_filepath = f"query_terms/query_terms_{query_terms_length}.json"

    with open(query_filepath, "r") as f:
        query_terms = json.load(f)

    output_dir_archives_all_articles = "archives_all_articles"
    os.makedirs(output_dir_archives_all_articles, exist_ok=True)

    output_dir_archives_top_articles = "archives_top_articles"
    os.makedirs(output_dir_archives_top_articles, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    # timestamp = "2025-07-14"
    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=7)

    all_newsapi_items = fetch_all_from_newsapi(
        query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
    )

    all_gdelt_items = fetch_all_from_gdelt(
        query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
    )

    df = normalize_and_merge(all_newsapi_items, all_gdelt_items)

    filename = f"all_articles_{timestamp}.csv"
    output_path = os.path.join(output_dir_archives_all_articles, filename)
    df.to_csv(output_path, index=True)

    query = "data procurement and data acquisition"

    articles_filtered = filter_articles(df)

    top_articles = get_relevant_articles(articles_filtered, query, 10)

    print(f"\nsummarizing top articles...\n")

    top_articles["summary"] = top_articles.apply(
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
    output_path = os.path.join(output_dir_archives_top_articles, filename)
    top_articles.to_csv(output_path, index=True)

    loaded_top_df_filename = (
        f"{output_dir_archives_top_articles}/top_articles_{timestamp}.csv"
    )
    loaded_top_df = pd.read_csv(loaded_top_df_filename)

    send_news_email(loaded_top_df, RECIPIENT_EMAIL)
    print(f"email sent successfully to {RECIPIENT_EMAIL}\n")

    export_standalone_html(loaded_top_df, timestamp=timestamp)


if __name__ == "__main__":

    print("\n--- starting Archie ---")
    start_time = time.time()

    main()

    end_time = time.time()
    print(f"--- Archie completed in {(end_time - start_time):.2f} seconds ---\n")
