import pandas as pd


def chunk_list(lst, chunk_size=6):

    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def normalize_and_merge(news_items, gdelt_items):

    combined = news_items + gdelt_items

    df = pd.DataFrame(combined)
    df["published_at_parsed"] = pd.to_datetime(df["published_at"], errors="coerce")
    df.sort_values("published_at_parsed", ascending=False, inplace=True)
    df.drop_duplicates(subset="url", keep="first", inplace=True)

    return df.sort_values("published_at_parsed", ascending=False).reset_index(drop=True)
