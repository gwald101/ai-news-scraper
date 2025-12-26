#!/usr/bin/env python3
"""
Run the full AI news scraper pipeline.

Usage:
    python run_all.py              # Run scrapers, aggregate, filter, and generate digest
    python run_all.py --sources x  # Only scrape from X (Twitter)
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
from pipeline.aggregate import aggregate_sources
from pipeline.filter import ContentFilter
from pipeline.digest import generate_digest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

SCRAPERS = {
    "x": XScraper,
    "instagram": InstagramScraper,
    "tiktok": TikTokScraper,
    "linkedin": LinkedInScraper,
    "web": WebScraper,
}


def main():
    parser = argparse.ArgumentParser(
        description="Run the full AI news aggregation pipeline"
    )
    parser.add_argument(
        "--sources",
        default=None,
        help="Comma-separated list of sources (default: all enabled)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config file"
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip scraping, use existing raw data"
    )
    parser.add_argument(
        "--skip-filter",
        action="store_true",
        help="Skip filtering and digest generation"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI News Scraper - Full Pipeline")
    logger.info("=" * 60)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Scrape content
    if not args.skip_scrape:
        logger.info("")
        logger.info("STEP 1: Scraping content")
        logger.info("-" * 40)
        
        if args.sources:
            source_list = [s.strip().lower() for s in args.sources.split(",")]
        else:
            source_list = list(SCRAPERS.keys())
        
        for source in source_list:
            if source not in SCRAPERS:
                logger.warning(f"Unknown source: {source}")
                continue
            
            scraper_class = SCRAPERS[source]
            scraper = scraper_class(config_path=args.config)
            
            try:
                scraper.run()
            except NotImplementedError:
                logger.info(f"{source}: not yet implemented, skipping")
            except Exception as e:
                logger.error(f"{source}: {e}")
    else:
        logger.info("Skipping scrape step (--skip-scrape)")
    
    # Step 2: Aggregate content
    logger.info("")
    logger.info("STEP 2: Aggregating content")
    logger.info("-" * 40)
    
    combined_data = aggregate_sources(output_dir)
    
    if not combined_data or not combined_data.get("items"):
        logger.warning("No content to process")
        return 0
    
    # Step 3: Filter and generate digest
    if not args.skip_filter:
        logger.info("")
        logger.info("STEP 3: Filtering content")
        logger.info("-" * 40)
        
        content_filter = ContentFilter(config_path=args.config)
        if not content_filter.initialize():
            logger.error("Failed to initialize filter")
            return 1
        
        items = combined_data.get("items", [])
        metadata = combined_data.get("metadata", {})
        
        filtered = content_filter.filter(items, metadata)
        content_filter.save_output(filtered)
        
        logger.info("")
        logger.info("STEP 4: Generating digest")
        logger.info("-" * 40)
        
        digest_path = generate_digest(filtered, output_dir)
        
        # Show summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"  Total items scraped: {len(items)}")
        logger.info(f"  NEWS items: {len(filtered.get('news', []))}")
        logger.info(f"  CHATTER items: {len(filtered.get('chatter', []))}")
        logger.info(f"  Digest: {digest_path}")
        logger.info("=" * 60)
    else:
        logger.info("Skipping filter step (--skip-filter)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

