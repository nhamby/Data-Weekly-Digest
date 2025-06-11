import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def get_relevant_articles(df: pd.DataFrame, query: str, top_n: int = 10):

    df["combined_text"] = (
        df["title"].fillna("") + ". " + df["description"].fillna("") + ". "
    )
    model_name = "all-MiniLM-L6-v2"
    print(f"Loading sentence transformer model {model_name}")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("model loaded")

    print("generating article embeddings")
    article_embeddings = model.encode(
        df["combined_text"].tolist(), show_progress_bar=True
    )
    print("article embeddings generated")

    print(f"generating query embedding")
    query_embedding = model.encode(query)
    print("query embedding generated.")

    similarity_scores = cosine_similarity(
        query_embedding.reshape(1, -1), article_embeddings
    ).flatten()

    df.loc[:, "relevance_score"] = similarity_scores

    relevant_articles = df.sort_values(by="relevance_score", ascending=False)

    return relevant_articles.head(top_n)
