# AI News Scraper

A multi-source content aggregator that discovers and curates AI-related news from social media and web sources.

## Features

- **Multi-source ingestion**: Supports X (Twitter), Instagram, TikTok, LinkedIn, and web/RSS
- **LLM-powered filtering**: Uses Gemini to classify content as "News" vs "Chatter"
- **Automated digest generation**: Creates markdown summaries organized by source and category
- **Modular architecture**: Easily add new sources or customize filtering

## Project Structure

```
ai-news-scraper/
├── config.yaml              # Central configuration
├── .env                     # API keys (not in repo)
├── requirements.txt         # Python dependencies
│
├── sources/                 # Account lists per platform
│   ├── x/users.json
│   ├── instagram/accounts.json
│   ├── tiktok/accounts.json
│   ├── linkedin/accounts.json
│   └── web/sources.json
│
├── scrapers/                # Source-specific scrapers
│   ├── base.py              # Abstract base class
│   ├── x.py                 # Twitter scraper (implemented)
│   ├── instagram.py         # Instagram (stub)
│   ├── tiktok.py            # TikTok (stub)
│   ├── linkedin.py          # LinkedIn (stub)
│   └── web.py               # RSS/Web (stub)
│
├── pipeline/                # Processing pipeline
│   ├── aggregate.py         # Combine sources
│   ├── filter.py            # LLM classification
│   └── digest.py            # Markdown generation
│
├── run_scrape.py            # Scrape content
├── run_filter.py            # Filter + generate digest
├── run_all.py               # Full pipeline
│
├── output/                  # Generated files (git-ignored)
│   ├── x_raw.json
│   ├── combined_raw.json
│   ├── filtered.json
│   └── digest.md
│
└── docs/                    # Documentation
    ├── PRD.md
    ├── IMPLEMENTATION_PLAN.md
    └── TASK_LIST.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file:

```
APIFY_API_TOKEN=your_apify_token
GEMINI_API_KEY=your_gemini_key
```

### 3. Add accounts to track

Edit `sources/x/users.json` with Twitter handles to follow:

```json
{
  "researchers": ["kaborat", "ylecun"],
  "companies_labs": ["OpenAI", "AnthropicAI"],
  "practitioners": ["levelsio"],
  "influencers": ["svpino"]
}
```

### 4. Run the pipeline

```bash
# Full pipeline: scrape → aggregate → filter → digest
python run_all.py

# Or run steps individually:
python run_scrape.py        # Scrape content
python run_filter.py        # Filter and generate digest

# Scrape specific sources only:
python run_scrape.py x      # Only Twitter
```

## Configuration

Edit `config.yaml` to customize:

```yaml
general:
  lookback_days: 7           # Only fetch content from last N days
  output_dir: "output"

llm:
  provider: "gemini"
  model: "gemini-1.5-flash"
  batch_size: 10

sources:
  x:
    enabled: true
    tweets_per_user: 20
  # Enable other sources as implemented
```

## Estimated Costs

- **X (Twitter)**: ~$0.50/month via Apify free tier
- **Gemini API**: Free tier (15 RPM, 1M tokens/day)
- **Total**: < $5/month for typical usage

## Adding New Sources

1. Create a new scraper in `scrapers/` extending `BaseScraper`
2. Add account list file in `sources/<source>/`
3. Update `config.yaml` with source settings
4. Register scraper in `scrapers/__init__.py` and CLI files

## License

MIT
