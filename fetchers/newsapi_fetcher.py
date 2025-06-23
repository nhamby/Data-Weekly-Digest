import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from helper_functions import chunk_list
from pprint import pprint
from urllib.parse import quote_plus


load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")


def fetch_chunk_from_newsapi(
    query_terms=None,
    page_size=50,
    from_date=None,
    to_date=None,
):

    if NEWSAPI_KEY is None:
        raise RuntimeError("NEWSAPI_KEY is not set in .env file")

    q_string = " OR ".join([f'"{term}"' for term in query_terms])

    if to_date is None:
        to_date = datetime.now(timezone.utc).date()
        
    if from_date is None:
        from_date = to_date - timedelta(days=7)

    url = (
        "https://newsapi.org/v2/everything?"
        f"q={quote_plus(q_string)}&"
        f"from={from_date.isoformat()}&"
        f"to={to_date.isoformat()}&"
        "language=en&"
        f"pageSize={page_size}&"
        "sortBy=publishedAt&"
        f"apiKey={NEWSAPI_KEY}"
    )

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

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


def fetch_all_from_newsapi(query_terms, chunk_size=6, from_date=None, to_date=None):

    all_newsapi_items = []

    print(f"\nFetching NewsAPI (from {from_date} to {to_date})...")

    for chunk in chunk_list(query_terms, chunk_size):

        try:
            items = fetch_chunk_from_newsapi(
                query_terms=chunk, from_date=from_date, to_date=to_date, page_size=50
            )
            all_newsapi_items.extend(items)

        except Exception as e:
            print(f"\tNewsAPI chunk error: {e}\n")

    print(f"\tTotal NewsAPI articles fetched: {len(all_newsapi_items)}\n")

    return all_newsapi_items
