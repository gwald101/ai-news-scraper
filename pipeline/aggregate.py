"""
Aggregation Module - combines content from all sources.

Reads raw output files from each scraper and combines them into
a single combined_raw.json file for filtering.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Mapping of source names to their raw output files
SOURCE_FILES = {
    "x": "x_raw.json",
    "instagram": "instagram_raw.json",
    "tiktok": "tiktok_raw.json",
    "linkedin": "linkedin_raw.json",
    "web": "web_raw.json",
}


def aggregate_sources(
    output_dir: Path = Path("output"),
    sources: Optional[List[str]] = None,
) -> Optional[Dict]:
    """
    Aggregate content from all source raw files.
    
    Args:
        output_dir: Directory containing raw output files
        sources: Optional list of sources to include (default: all available)
        
    Returns:
        Dict with combined items and metadata, or None if no data found
    """
    output_dir = Path(output_dir)
    
    if sources is None:
        sources = list(SOURCE_FILES.keys())
    
    all_items = []
    source_stats = {}
    earliest_date = None
    latest_date = None
    
    for source in sources:
        filename = SOURCE_FILES.get(source)
        if not filename:
            logger.warning(f"Unknown source: {source}")
            continue
        
        filepath = output_dir / filename
        
        if not filepath.exists():
            logger.debug(f"No data file for {source}: {filepath}")
            continue
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            items = data.get("items", [])
            metadata = data.get("metadata", {})
            
            # Track stats
            source_stats[source] = len(items)
            all_items.extend(items)
            
            # Track date range
            date_range = metadata.get("date_range", {})
            if date_range.get("from"):
                from_date = date_range["from"]
                if earliest_date is None or from_date < earliest_date:
                    earliest_date = from_date
            if date_range.get("to"):
                to_date = date_range["to"]
                if latest_date is None or to_date > latest_date:
                    latest_date = to_date
            
            logger.info(f"Loaded {len(items)} items from {source}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")
    
    # Also check for legacy raw_tweets.json
    legacy_file = Path("raw_tweets.json")
    if legacy_file.exists() and "x" not in source_stats:
        try:
            with open(legacy_file, "r") as f:
                data = json.load(f)
            
            tweets = data.get("tweets", [])
            # Add source field to legacy tweets
            for tweet in tweets:
                tweet["source"] = "x"
            
            all_items.extend(tweets)
            source_stats["x (legacy)"] = len(tweets)
            
            metadata = data.get("metadata", {})
            date_range = metadata.get("date_range", {})
            if date_range.get("from"):
                from_date = date_range["from"]
                if earliest_date is None or from_date < earliest_date:
                    earliest_date = from_date
            if date_range.get("to"):
                to_date = date_range["to"]
                if latest_date is None or to_date > latest_date:
                    latest_date = to_date
            
            logger.info(f"Loaded {len(tweets)} items from legacy raw_tweets.json")
            
        except Exception as e:
            logger.warning(f"Failed to load legacy file: {e}")
    
    if not all_items:
        logger.warning("No content found from any source")
        return None
    
    # Sort by date (newest first)
    all_items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Build combined output
    combined = {
        "metadata": {
            "aggregated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(all_items),
            "sources": source_stats,
            "date_range": {
                "from": earliest_date,
                "to": latest_date,
            },
        },
        "items": all_items,
    }
    
    # Save combined file
    combined_file = output_dir / "combined_raw.json"
    with open(combined_file, "w") as f:
        json.dump(combined, f, indent=2)
    
    logger.info(f"Aggregated {len(all_items)} items from {len(source_stats)} sources")
    logger.info(f"Saved to {combined_file}")
    
    return combined


# CLI entry point
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    result = aggregate_sources()
    
    if result:
        print(f"\nAggregated {result['metadata']['total_items']} items")
        print(f"Sources: {result['metadata']['sources']}")
    else:
        print("No content to aggregate")

