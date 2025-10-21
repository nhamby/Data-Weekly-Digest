"""GDELT fetcher for article retrieval."""

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Any

import requests
from dotenv import load_dotenv

from helper_functions import chunk_list

logger = logging.getLogger(__name__)

load_dotenv()
GDELT_API_ENDPOINT = os.getenv("GDELT_API_ENDPOINT")

# Constants
DEFAULT_MAX_RECORDS = 50


def fetch_chunk_from_gdelt(
    query_terms: List[str] | None = None,
    maxrecords: int = DEFAULT_MAX_RECORDS,
    from_date: date | None = None,
    to_date: date | None = None,
) -> List[Dict[str, Any]]:
    """Fetch a chunk of articles from GDELT.

    Args:
        query_terms: List of search terms
        maxrecords: Maximum number of articles to fetch
        from_date: Start date for article search
        to_date: End date for article search

    Returns:
        List of normalized article dictionaries

    Raises:
        ValueError: If query_terms is None
        RuntimeError: If GDELT_API_ENDPOINT is not set
    """
    if query_terms is None:
        raise ValueError("query_terms cannot be None")

    if GDELT_API_ENDPOINT is None:
        raise RuntimeError("GDELT_API_ENDPOINT is not set in .env file")

    # Quote terms with spaces
    quoted_terms = [f'"{term}"' if " " in term else term for term in query_terms]
    or_joined = "(" + " OR ".join(quoted_terms) + ")"

    if to_date is None:
        to_date = datetime.now(timezone.utc).date()

    if from_date is None:
        from_date = to_date - timedelta(days=7)

    # GDELT uses specific datetime format: YYYYMMDDhhmmss
    start_str = from_date.strftime("%Y%m%d") + "000000"
    end_str = to_date.strftime("%Y%m%d") + "235959"

    params = {
        "query": or_joined,
        "mode": "ArtList",
        "maxrecords": maxrecords,
        "format": "json",
        "startdatetime": start_str,
        "enddatetime": end_str,
    }

    try:
        resp = requests.get(GDELT_API_ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"GDELT request failed: {e}")
        raise

    normalized = []

    for article in data.get("articles", []):
        # Parse GDELT's datetime format
        seen_date = article.get("seendate", "")
        seen_time = article.get("seentime", "")
        published_at = ""

        if seen_date and seen_time:
            # Convert YYYYMMDDhhmmss to ISO format
            published_at = (
                f"{seen_date[:4]}-{seen_date[4:6]}-{seen_date[6:]}T"
                f"{seen_time[:2]}:{seen_time[2:4]}:{seen_time[4:]}Z"
            )

        normalized.append(
            {
                "source": article.get("domain", "GDELT"),
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "published_at": published_at,
                "description": article.get("domain", ""),
                "content": article.get("seendate", ""),
                "fetched_from": "gdelt",
            }
        )

    return normalized


def fetch_all_from_gdelt(
    query_terms: List[str],
    chunk_size: int = 6,
    from_date: date | None = None,
    to_date: date | None = None,
) -> List[Dict[str, Any]]:
    """Fetch all articles from GDELT using chunked queries.

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
    all_gdelt_items = []

    logger.info(f"Fetching GDELT (from {from_date} to {to_date})...")

    for chunk in chunk_list(query_terms, chunk_size):
        try:
            items = fetch_chunk_from_gdelt(
                query_terms=chunk,
                maxrecords=DEFAULT_MAX_RECORDS,
                from_date=from_date,
                to_date=to_date,
            )
            all_gdelt_items.extend(items)
            logger.debug(f"Fetched {len(items)} articles from chunk")

        except Exception as e:
            logger.error(f"GDELT chunk error: {e}")

    logger.info(f"Total GDELT articles fetched: {len(all_gdelt_items)}")

    return all_gdelt_items
