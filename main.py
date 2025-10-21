"""
Archie's Data Weekly Digest

An automated news aggregation and curation system that fetches, filters,
and summarizes the most relevant tech and data industry articles from
multiple sources, then delivers them via email.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from fetchers.gdelt_fetcher import fetch_all_from_gdelt
from fetchers.newsapi_fetcher import fetch_all_from_newsapi
from helper_functions import normalize_and_merge
from html_and_email_functions import (
    RECIPIENT_EMAIL,
    export_standalone_html,
    send_news_email,
)
from semantic_similarity import filter_articles, get_relevant_articles
from summarize_articles import summarize_article_gemini

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_query_terms(query_terms_length: str) -> list:
    """Load query terms from JSON file.

    Args:
        query_terms_length: Either 'short' or 'long'

    Returns:
        List of query terms

    Raises:
        FileNotFoundError: If query terms file doesn't exist
    """
    query_filepath = Path(f"query_terms/query_terms_{query_terms_length}.json")

    if not query_filepath.exists():
        raise FileNotFoundError(
            f"Query terms file not found: {query_filepath}. "
            f"Available options: 'short' or 'long'"
        )

    with open(query_filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main(
    days: int = 6, article_count: int = 10, query_terms_length: str = "short"
) -> None:
    """Main execution function for Archie's digest.

    Args:
        days: Number of days to look back for articles
        article_count: Number of top articles to include in digest
        query_terms_length: Which query terms file to use ('short' or 'long')

    Raises:
        RuntimeError: If required environment variables are not set
    """
    try:
        # Load query terms
        query_terms = load_query_terms(query_terms_length)

        # Setup output directories
        output_dir_archives_all_articles = Path("archives_all_articles")
        output_dir_archives_all_articles.mkdir(exist_ok=True)

        output_dir_archives_top_articles = Path("archives_top_articles")
        output_dir_archives_top_articles.mkdir(exist_ok=True)

        # Setup dates
        timestamp = datetime.now().strftime("%Y-%m-%d")
        to_date = datetime.now(timezone.utc).date()
        from_date = to_date - timedelta(days=days)

        logger.info(f"Fetching articles from {from_date} to {to_date} ({days} days)")
        logger.info(f"Using query terms: {query_terms_length}")
        logger.info(f"Will select top {article_count} articles")

        # Fetch articles from multiple sources
        all_newsapi_items = fetch_all_from_newsapi(
            query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
        )

        all_gdelt_items = fetch_all_from_gdelt(
            query_terms=query_terms, chunk_size=6, from_date=from_date, to_date=to_date
        )

        # Normalize and merge articles
        df = normalize_and_merge(all_newsapi_items, all_gdelt_items)
        logger.info(f"Total articles fetched: {len(df)}")

        # Save all articles
        all_articles_path = (
            output_dir_archives_all_articles / f"all_articles_{timestamp}.csv"
        )
        df.to_csv(all_articles_path, index=True)
        logger.info(f"Saved all articles to {all_articles_path}")

        # Filter and rank articles
        query = "data procurement and data acquisition"
        articles_filtered = filter_articles(df)
        logger.info(f"Articles after filtering: {len(articles_filtered)}")

        top_articles = get_relevant_articles(articles_filtered, query, article_count)
        logger.info(f"Selected top {article_count} articles")

        # Summarize articles
        logger.info(f"Summarizing top {article_count} articles...")
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

        # Save top articles
        top_articles_path = (
            output_dir_archives_top_articles / f"top_articles_{timestamp}.csv"
        )
        top_articles.to_csv(top_articles_path, index=True)
        logger.info(f"Saved top articles to {top_articles_path}")

        # Send email
        if RECIPIENT_EMAIL is None:
            raise RuntimeError("RECIPIENT_EMAIL is not set in .env file")

        send_news_email(top_articles, RECIPIENT_EMAIL)
        logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")

        # Export HTML
        html_path = export_standalone_html(top_articles, timestamp=timestamp)
        logger.info(f"Exported HTML digest to {html_path}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Archie's Data Weekly Digest - Automated news aggregation and curation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Use all defaults
  python main.py --days 14                         # Fetch articles from last 14 days
  python main.py --count 15                        # Get top 15 articles
  python main.py --query-terms long                # Use comprehensive search terms
  python main.py --days 30 --count 20 --query-terms long  # Combine multiple flags
        """,
    )

    parser.add_argument(
        "--days",
        type=int,
        default=6,
        help="Number of days to look back for articles (default: 6)",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of top articles to include in digest (default: 10)",
    )

    parser.add_argument(
        "--query-terms",
        type=str,
        default="short",
        choices=["short", "long"],
        help="Which query terms file to use: 'short' or 'long' (default: short)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    logger.info("Starting Archie")
    start_time = time.time()

    try:
        args = parse_arguments()
        main(
            days=args.days,
            article_count=args.count,
            query_terms_length=args.query_terms,
        )

        elapsed_time = time.time() - start_time
        logger.info(f"Archie completed successfully in {elapsed_time:.2f} seconds")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Archie failed: {e}")
        sys.exit(1)
