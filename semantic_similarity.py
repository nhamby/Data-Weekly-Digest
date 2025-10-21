"""Semantic similarity functions for article ranking and filtering."""

import logging
import os
from typing import List

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Prevent tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "all-MiniLM-L6-v2"
FILTERED_SOURCES = ["Pypi.org", "Fox News", "W3.org"]


def get_relevant_articles(
    df: pd.DataFrame, query: str, top_n: int = 10
) -> pd.DataFrame:
    """Find and rank articles most relevant to a query using semantic similarity.

    Uses sentence transformers to generate embeddings and cosine similarity
    to rank articles by relevance to the query.

    Args:
        df: DataFrame containing articles with 'title' and 'description' columns
        query: Search query to match against
        top_n: Number of top articles to return

    Returns:
        DataFrame with top N articles sorted by relevance score
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to get_relevant_articles")
        return df

    # Combine title and description for better matching
    df = df.copy()
    df["combined_text"] = (
        df["title"].fillna("") + ". " + df["description"].fillna("") + ". "
    )

    logger.info(f"Loading sentence transformer model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    logger.info("Generating article embeddings...")
    article_embeddings = model.encode(
        df["combined_text"].tolist(), show_progress_bar=True
    )

    query_embedding = model.encode(query)

    # Convert tensors to numpy arrays for sklearn compatibility
    query_embedding_np = np.array(query_embedding)
    article_embeddings_np = np.array(article_embeddings)

    similarity_scores = cosine_similarity(
        query_embedding_np.reshape(1, -1), article_embeddings_np
    ).flatten()

    df["relevance_score"] = similarity_scores

    relevant_articles = df.sort_values(by="relevance_score", ascending=False)

    return relevant_articles.head(top_n)


def filter_articles(
    articles: pd.DataFrame, excluded_sources: List[str] | None = None
) -> pd.DataFrame:
    """Filter out articles from specified sources.

    Args:
        articles: DataFrame containing articles with 'source' column
        excluded_sources: List of source names to exclude (uses default if None)

    Returns:
        Filtered DataFrame with excluded sources removed
    """
    if excluded_sources is None:
        excluded_sources = FILTERED_SOURCES

    if articles.empty:
        logger.warning("Empty DataFrame provided to filter_articles")
        return articles

    filtered = articles[~articles["source"].isin(excluded_sources)].copy()
    filtered.reset_index(drop=True, inplace=True)

    logger.info(
        f"Filtered {len(articles) - len(filtered)} articles from sources: {excluded_sources}"
    )

    return filtered
