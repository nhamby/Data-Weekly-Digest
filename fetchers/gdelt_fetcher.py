import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from helper_functions import chunk_list

load_dotenv()
GDELT_API_ENDPOINT = os.getenv("GDELT_API_ENDPOINT")


def fetch_chunk_from_gdelt(
    query_terms=None,
    maxrecords=50,
    from_date=None,
    to_date=None,
):

    quoted_terms = [f'"{term}"' if " " in term else term for term in query_terms]
    or_joined = "(" + " OR ".join(quoted_terms) + ")"

    if to_date is None:
        to_date = datetime.now(timezone.utc).date()

    if from_date is None:
        from_date = to_date - timedelta(days=7)

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

    resp = requests.get(GDELT_API_ENDPOINT, params=params)
    resp.raise_for_status()
    data = resp.json()

    normalized = []

    for article in data.get("articles", []):
        seen_date = article.get("seendate", "")
        seen_time = article.get("seentime", "")
        published_at = ""
        if seen_date and seen_time:
            published_at = (
                seen_date[:4]
                + "-"
                + seen_date[4:6]
                + "-"
                + seen_date[6:]
                + "T"
                + seen_time[:2]
                + ":"
                + seen_time[2:4]
                + ":"
                + seen_time[4:]
                + "Z"
            )

        normalized.append(
            {
                "source": article.get("domain", "GDELT"),
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "published_at": published_at,
                "description": article.get("domain", ""),
                "content": article.get(
                    "seendate", ""
                ),  # placeholder; we can fetch full text later if needed
                "fetched_from": "gdelt",
            }
        )

    return normalized


def fetch_all_from_gdelt(query_terms, chunk_size=6, from_date=None, to_date=None):

    all_gdelt_items = []

    print(f"fetching GDELT (from {from_date} to {to_date})...")

    for chunk in chunk_list(query_terms, chunk_size):

        try:
            items = fetch_chunk_from_gdelt(
                query_terms=chunk, maxrecords=50, from_date=from_date, to_date=to_date
            )
            all_gdelt_items.extend(items)

        except Exception as e:
            print(f"\tGDELT chunk error: {e}\n")

    print(f"\ttotal GDELT articles fetched: {len(all_gdelt_items)}\n")

    return all_gdelt_items
