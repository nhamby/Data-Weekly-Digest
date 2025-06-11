import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def summarize_article_gemini(
    source: str, title: str, url: str, published_at: str, description: str, content: str
) -> str:

    prompt = f"""
    Please summarize the following article concisely. Focus on two main points, each with their own sentence. Do not provide any additional commentary or trailing newline characters.

    Article Details:
    - Source: {source}
    - Title: {title}
    - Published On: {published_at}
    - URL: {url}
    - Description: {description}

    Full Content:
    {content}

    ---
    Summary:
    """

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)

    return response.text
