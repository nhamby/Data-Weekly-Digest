"""Helper utility functions for article processing."""

from typing import Generator, List, Dict, Any

import pandas as pd


def chunk_list(lst: List[Any], chunk_size: int = 6) -> Generator[List[Any], None, None]:
    """Split a list into chunks of specified size.

    Args:
        lst: List to be chunked
        chunk_size: Size of each chunk

    Yields:
        Chunks of the original list
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def normalize_and_merge(
    news_items: List[Dict[str, Any]], gdelt_items: List[Dict[str, Any]]
) -> pd.DataFrame:
    """Normalize and merge articles from different sources.

    Combines articles from NewsAPI and GDELT, removes duplicates,
    and sorts by publication date.

    Args:
        news_items: Articles from NewsAPI
        gdelt_items: Articles from GDELT

    Returns:
        DataFrame with normalized and deduplicated articles
    """
    combined = news_items + gdelt_items

    df = pd.DataFrame(combined)
    df["published_at_parsed"] = pd.to_datetime(df["published_at"], errors="coerce")
    df = df.sort_values("published_at_parsed", ascending=False)
    df = df.drop_duplicates(subset="url", keep="first")

    return df.sort_values("published_at_parsed", ascending=False).reset_index(drop=True)
