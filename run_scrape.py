#!/usr/bin/env python3
"""
Run content scrapers.

Usage:
    python run_scrape.py           # Run all enabled scrapers
    python run_scrape.py x         # Run only X (Twitter) scraper
    python run_scrape.py x,web     # Run specific scrapers
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import XScraper
from scrapers.instagram import InstagramScraper
from scrapers.tiktok import TikTokScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.web import WebScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Available scrapers
SCRAPERS = {
    "x": XScraper,
    "instagram": InstagramScraper,
    "tiktok": TikTokScraper,
    "linkedin": LinkedInScraper,
    "web": WebScraper,
}


def main():
    parser = argparse.ArgumentParser(
        description="Run content scrapers for AI news aggregation"
    )
    parser.add_argument(
        "sources",
        nargs="?",
        default=None,
        help="Comma-separated list of sources to scrape (e.g., 'x,web'). Defaults to all enabled."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config file (default: config.yaml)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI News Scraper - Content Ingestion")
    logger.info("=" * 60)
    
    # Determine which scrapers to run
    if args.sources:
        source_list = [s.strip().lower() for s in args.sources.split(",")]
    else:
        source_list = list(SCRAPERS.keys())
    
    # Validate sources
    invalid = [s for s in source_list if s not in SCRAPERS]
    if invalid:
        logger.error(f"Unknown sources: {', '.join(invalid)}")
        logger.error(f"Valid sources: {', '.join(SCRAPERS.keys())}")
        return 1
    
    # Run scrapers
    results = {}
    for source in source_list:
        scraper_class = SCRAPERS[source]
        scraper = scraper_class(config_path=args.config)
        
        try:
            output_path = scraper.run()
            results[source] = "success" if output_path else "skipped/disabled"
        except NotImplementedError:
            logger.warning(f"{source} scraper not yet implemented")
            results[source] = "not implemented"
        except Exception as e:
            logger.error(f"{source} scraper failed: {e}")
            results[source] = f"error: {e}"
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SCRAPING COMPLETE")
    for source, result in results.items():
        logger.info(f"  {source}: {result}")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

