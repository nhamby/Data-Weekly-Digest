"""Article summarization using Google Gemini AI."""

import logging
import os

from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env file")

client = genai.Client(api_key=GEMINI_API_KEY)

# Constants
GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_SUMMARY = "Summary not available."


def summarize_article_gemini(
    source: str,
    title: str,
    url: str,
    published_at: str,
    description: str,
    content: str,
) -> str:
    """Generate an AI summary of an article using Google Gemini.

    Creates a concise summary focused on key takeaways for data startups,
    including important metrics and statistics.

    Args:
        source: Article source name
        title: Article title
        url: Article URL (not currently used in prompt)
        published_at: Publication date (not currently used in prompt)
        description: Article description/excerpt
        content: Full article content

    Returns:
        AI-generated summary or default message if generation fails
    """
    prompt = f"""
Please summarize the following article concisely but thoroughly, with a focus on \
the takeaways relevant to a data startup. Focus on three main points, preferably \
with a detailed sentence for each. Sentences should be no longer than 20 words but \
no shorter than 10. Try to include key metrics such as percentages, statistics, or \
any numerical data of importance. Do not provide any additional commentary or \
trailing newline characters.

Article Details:
- Source: {source}
- Title: {title}
- Description: {description}

Full Content:
{content}

---
Summary:
"""

    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)

        if response.text is None:
            logger.warning(f"No summary generated for article: {title}")
            return DEFAULT_SUMMARY

        return response.text.strip()

    except Exception as e:
        logger.error(f"Error summarizing article '{title}': {e}")
        return DEFAULT_SUMMARY
