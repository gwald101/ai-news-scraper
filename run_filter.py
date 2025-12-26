#!/usr/bin/env python3
"""
Run the content filter and generate digest.

Usage:
    python run_filter.py           # Filter content and generate digest
    python run_filter.py --no-digest  # Filter only, skip digest generation
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.filter import ContentFilter, load_combined_content
from pipeline.digest import generate_digest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Filter scraped content using LLM and generate digest"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config file (default: config.yaml)"
    )
    parser.add_argument(
        "--no-digest",
        action="store_true",
        help="Skip digest generation"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI News Scraper - Intelligence Module")
    logger.info("=" * 60)
    
    # Load content
    data = load_combined_content(args.output_dir)
    if not data:
        logger.error("No content found. Run scrapers first.")
        return 1
    
    items = data.get("items", [])
    metadata = data.get("metadata", {})
    
    if not items:
        logger.warning("No items to filter")
        return 0
    
    logger.info(f"Loaded {len(items)} items to filter")
    
    # Initialize filter
    content_filter = ContentFilter(config_path=args.config)
    if not content_filter.initialize():
        return 1
    
    # Run filter
    filtered = content_filter.filter(items, metadata)
    content_filter.save_output(filtered)
    
    # Generate digest
    if not args.no_digest:
        digest_path = generate_digest(filtered, args.output_dir)
        logger.info(f"Generated digest at {digest_path}")
        
        # Preview
        with open(digest_path, "r") as f:
            preview = f.read()
        
        print(f"\n{'=' * 60}")
        print("DIGEST PREVIEW")
        print(f"{'=' * 60}\n")
        print(preview[:1500])
        if len(preview) > 1500:
            print(f"\n... (see {digest_path} for full digest)")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("FILTERING COMPLETE")
    logger.info(f"  NEWS items: {len(filtered.get('news', []))}")
    logger.info(f"  CHATTER items: {len(filtered.get('chatter', []))}")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

