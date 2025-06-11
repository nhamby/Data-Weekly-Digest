import os
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chunk_text(text, max_tokens=1000):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    return [
        encoding.decode(tokens[i : i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]


def summarize_with_openai(text):
    parts = list(chunk_text(text))
    summaries = []
    for part in parts:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that concisely summarizes text.",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following article in 3-4 sentences, highlighting key takeaways and insightful statistics:\n\n{part}",
                },
            ],
            temperature=0.2,
            max_tokens=150,
        )
        summaries.append(resp.choices[0].message.content.strip())
    if len(summaries) > 1:
        combined = " ".join(summaries)
        resp2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that concisely summarizes text.",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following articles in 3-4 sentences, highlighting key takeaways and insightful statistics:\n\n{combined}",
                },
            ],
            temperature=0.2,
            max_tokens=150,
        )
        return resp2.choices[0].message.content.strip()
    else:
        return summaries[0]
