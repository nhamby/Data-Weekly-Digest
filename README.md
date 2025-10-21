# Archie's Data Weekly Digest

An automated news aggregation and curation system that fetches, filters, and summarizes the most relevant tech and data industry articles from multiple sources, then delivers them via email as a beautifully formatted weekly digest.

## What It Does

**Archie** is your AI-powered news curator that:

1. **Fetches Articles** - Pulls news from NewsAPI and GDELT based on customizable search terms
2. **Filters & Ranks** - Uses semantic similarity to find articles most relevant to data procurement and acquisition
3. **Summarizes** - Leverages Google Gemini AI to create concise, actionable summaries
4. **Delivers** - Sends a beautifully formatted HTML email digest with the top 10 articles
5. **Archives** - Saves all articles and digests for future reference

## Features

- **Multi-source aggregation** from NewsAPI and GDELT
- **AI-powered semantic search** using sentence transformers
- **Smart summarization** with Google Gemini
- **Beautiful HTML email** with embedded logos and responsive design
- **Automatic archiving** of articles and HTML digests
- **Customizable search terms** via JSON configuration

## Project Structure

```text
├── main.py                          # Main orchestration script
├── fetchers/
│   ├── newsapi_fetcher.py          # NewsAPI integration
│   └── gdelt_fetcher.py            # GDELT integration
├── semantic_similarity.py          # Article ranking via embeddings
├── summarize_articles.py           # AI summarization with Gemini
├── html_and_email_functions.py    # Email formatting and sending
├── helper_functions.py             # Utility functions
├── query_terms/
│   ├── query_terms_short.json     # Concise search terms
│   └── query_terms_long.json      # Comprehensive search terms
├── archives_all_articles/          # All fetched articles (CSV)
├── archives_top_articles/          # Top-ranked articles (CSV)
├── archives_html/                  # HTML email archives
└── logos/                          # Email logo assets
```

## Setup

### Prerequisites

- Python 3.8+
- Gmail account (for sending emails)
- API keys for:
  - [NewsAPI](https://newsapi.org/)
  - [Google Gemini](https://ai.google.dev/)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd "Data Weekly Digest"
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy the example file:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:

   ```env
   GDELT_API_ENDPOINT="https://api.gdeltproject.org/api/v2/doc/doc"
   NEWSAPI_KEY=your_newsapi_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GMAIL_EMAIL_ADDRESS=your_email@gmail.com
   GMAIL_APP_PASSWORD=your_app_specific_password
   RECIPIENT_EMAIL=recipient@example.com
   ```

   **Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

## Usage

### Run the Digest

Simply execute the main script with default settings:

```bash
python main.py
```

This will:

1. Fetch articles from the past 6 days
2. Rank and select the top 10 most relevant articles
3. Generate AI summaries for each article
4. Send an email digest
5. Save archives in CSV and HTML formats

### Command-Line Flags

Customize Archie's behavior using command-line flags:

```bash
# Use all defaults (6 days, 10 articles, short query terms)
python main.py

# Fetch articles from the last 14 days
python main.py --days 14

# Get top 15 articles instead of 10
python main.py --count 15

# Use comprehensive search terms instead of short
python main.py --query-terms long

# Combine multiple flags
python main.py --days 30 --count 20 --query-terms long
```

#### Available Flags

- `--days N` - Number of days to look back for articles (default: 6)
- `--count N` - Number of top articles to include in digest (default: 10)
- `--query-terms {short|long}` - Which query terms file to use (default: short)

### Customize Search Terms

Edit the query terms files to focus on topics relevant to your interests:

- `query_terms/query_terms_short.json` - Quick, focused searches
- `query_terms/query_terms_long.json` - Comprehensive coverage

You can switch between them using the `--query-terms` flag as shown above.

## Output

### Email Digest

A formatted HTML email containing:

- Top 10 curated articles
- AI-generated summaries
- Direct links to original articles
- Source attribution

### Archived Files

- **All Articles CSV**: `archives_all_articles/all_articles_YYYY-MM-DD.csv`
- **Top Articles CSV**: `archives_top_articles/top_articles_YYYY-MM-DD.csv`
- **HTML Digest**: `archives_html/archie_digest_YYYY-MM-DD.html`

## How It Works

### 1. Article Fetching

Archie queries both NewsAPI and GDELT APIs with your search terms, pulling articles from the past week.

### 2. Semantic Ranking

Using the `sentence-transformers` library, Archie:

- Generates embeddings for each article's title and description
- Compares them to a target query using cosine similarity
- Ranks articles by relevance score

### 3. AI Summarization

Each top article is sent to Google Gemini with a prompt to:

- Extract key takeaways relevant to data startups
- Include important metrics and statistics
- Generate 3 concise points (10-20 words each)

### 4. Email Delivery

The formatted digest is sent via Gmail SMTP with:

- Responsive HTML design
- Embedded logos using CID
- Professional styling with gradients and colors

## Troubleshooting

### Common Issues

#### "RuntimeError: NEWSAPI_KEY is not set in .env file"

- Make sure your `.env` file exists and contains all required variables
- Check that variable names match exactly (case-sensitive)

#### "SMTPAuthenticationError"

- Ensure you're using a Gmail App Password, not your regular password
- Verify that 2-factor authentication is enabled on your Gmail account

#### "No articles found"

- Try different search terms or expand your query list
- Increase the time range (more than 7 days)
- Check API key limits and quotas

#### Semantic similarity errors

- The first run downloads the sentence transformer model (may take time)
- Ensure you have sufficient disk space (~400MB for the model)

## Dependencies

Key libraries used:

- `sentence-transformers` - Semantic article ranking
- `google-genai` - AI-powered summarization
- `pandas` - Data manipulation and CSV handling
- `scikit-learn` - Cosine similarity calculations
- `requests` - API interactions
- `python-dotenv` - Environment variable management

## Contributing

Feel free to open issues or submit pull requests for:

- Additional news sources
- Improved ranking algorithms
- Enhanced email templates
- Bug fixes and optimizations
