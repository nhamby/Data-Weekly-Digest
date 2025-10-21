"""NewsAPI fetcher for article retrieval."""

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Any
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv

from helper_functions import chunk_list

logger = logging.getLogger(__name__)

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Constants
NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
DEFAULT_PAGE_SIZE = 50
DEFAULT_LANGUAGE = "en"


def fetch_chunk_from_newsapi(
    query_terms: List[str] | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    from_date: date | None = None,
    to_date: date | None = None,
) -> List[Dict[str, Any]]:
    """Fetch a chunk of articles from NewsAPI.

    Args:
        query_terms: List of search terms
        page_size: Number of articles to fetch
        from_date: Start date for article search
        to_date: End date for article search

    Returns:
        List of normalized article dictionaries

    Raises:
        RuntimeError: If NEWSAPI_KEY is not set
        ValueError: If query_terms is None
    """
    if NEWSAPI_KEY is None:
        raise RuntimeError("NEWSAPI_KEY is not set in .env file")

    if query_terms is None:
        raise ValueError("query_terms cannot be None")

    q_string = " OR ".join([f'"{term}"' for term in query_terms])

    if to_date is None:
        to_date = datetime.now(timezone.utc).date()

    if from_date is None:
        from_date = to_date - timedelta(days=7)

    # Build URL with parameters
    url = (
        f"{NEWSAPI_BASE_URL}?"
        f"q={quote_plus(q_string)}&"
        f"from={from_date.isoformat()}&"
        f"to={to_date.isoformat()}&"
        f"language={DEFAULT_LANGUAGE}&"
        f"pageSize={page_size}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWSAPI_KEY}"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"NewsAPI request failed: {e}")
        raise

    normalized = []
    for article in data.get("articles", []):
        normalized.append(
            {
                "source": article["source"]["name"],
                "title": article["title"] or "",
                "url": article["url"],
                "published_at": article["publishedAt"],
                "description": article.get("description") or "",
                "content": article.get("content") or "",
                "fetched_from": "newsapi",
            }
        )

    return normalized


def fetch_all_from_newsapi(
    query_terms: List[str],
    chunk_size: int = 6,
    from_date: date | None = None,
    to_date: date | None = None,
) -> List[Dict[str, Any]]:
    """Fetch all articles from NewsAPI using chunked queries.

    Splits query terms into chunks to avoid API limitations and fetches
    articles for each chunk.

    Args:
        query_terms: List of search terms
        chunk_size: Number of terms to include per API request
        from_date: Start date for article search
        to_date: End date for article search

    Returns:
        List of all fetched articles
    """
    all_newsapi_items = []

    logger.info(f"Fetching NewsAPI (from {from_date} to {to_date})...")

    for chunk in chunk_list(query_terms, chunk_size):
        try:
            items = fetch_chunk_from_newsapi(
                query_terms=chunk,
                from_date=from_date,
                to_date=to_date,
                page_size=DEFAULT_PAGE_SIZE,
            )
            all_newsapi_items.extend(items)
            logger.debug(f"Fetched {len(items)} articles from chunk")

        except Exception as e:
            logger.error(f"NewsAPI chunk error: {e}")

    logger.info(f"Total NewsAPI articles fetched: {len(all_newsapi_items)}")

    return all_newsapi_items
