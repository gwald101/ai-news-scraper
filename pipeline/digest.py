"""
Digest Generator - creates markdown digest from filtered content.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import yaml

logger = logging.getLogger(__name__)


# Source display configuration
SOURCE_ICONS = {
    "x": "𝕏",
    "instagram": "📸",
    "tiktok": "🎵",
    "linkedin": "💼",
    "web": "🌐",
}

SOURCE_NAMES = {
    "x": "X (Twitter)",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "linkedin": "LinkedIn",
    "web": "Web / RSS",
}

CATEGORY_ICONS = {
    "researchers": "🔬",
    "companies_labs": "🏢",
    "practitioners": "⚙️",
    "influencers": "📢",
    "unknown": "📌",
    "uncategorized": "📌",
}

CATEGORY_TITLES = {
    "researchers": "Research & Academia",
    "companies_labs": "Companies & Labs",
    "practitioners": "Practitioners & Builders",
    "influencers": "Influencers & Educators",
    "unknown": "Other",
    "uncategorized": "Other",
}


def generate_digest(
    filtered_data: Dict,
    output_dir: Path = Path("output"),
) -> Path:
    """
    Generate a markdown digest from filtered content.
    
    Args:
        filtered_data: Dict with 'news', 'chatter', and 'metadata' keys
        output_dir: Directory to save the digest
        
    Returns:
        Path to the generated digest file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    news_items = filtered_data.get("news", [])
    metadata = filtered_data.get("metadata", {})
    
    # Extract date range
    date_range = metadata.get("date_range", {})
    from_date = date_range.get("from", "")[:10]
    to_date = date_range.get("to", "")[:10]
    
    lines = [
        "# AI News Digest",
        "",
        f"**Period:** {from_date} to {to_date}",
        f"**Total content analyzed:** {metadata.get('total_items', metadata.get('total_tweets', 0))}",
        f"**News items found:** {len(news_items)}",
        "",
        "---",
        "",
    ]
    
    # Group by source first, then by category
    by_source = {}
    for item in news_items:
        source = item.get("source", "unknown")
        if source not in by_source:
            by_source[source] = {}
        
        category = item.get("category", "unknown")
        if category not in by_source[source]:
            by_source[source][category] = []
        
        by_source[source][category].append(item)
    
    # Source order
    source_order = ["x", "instagram", "tiktok", "linkedin", "web"]
    category_order = ["researchers", "companies_labs", "practitioners", "influencers", "unknown", "uncategorized"]
    
    for source in source_order:
        if source not in by_source:
            continue
        
        source_icon = SOURCE_ICONS.get(source, "📄")
        source_name = SOURCE_NAMES.get(source, source)
        
        lines.append(f"## {source_icon} {source_name}")
        lines.append("")
        
        categories = by_source[source]
        
        for category in category_order:
            if category not in categories:
                continue
            
            items = categories[category]
            cat_icon = CATEGORY_ICONS.get(category, "📌")
            cat_title = CATEGORY_TITLES.get(category, category)
            
            lines.append(f"### {cat_icon} {cat_title}")
            lines.append("")
            
            for item in items:
                lines.extend(_format_item(item, source))
            
            lines.append("")
        
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    
    # Write to file
    output_file = output_dir / "digest.md"
    content = "\n".join(lines)
    
    with open(output_file, "w") as f:
        f.write(content)
    
    logger.info(f"Generated digest with {len(news_items)} news items")
    return output_file


def _format_item(item: Dict, source: str) -> List[str]:
    """Format a single item for the digest."""
    lines = []
    
    username = item.get("username", "unknown")
    summary = item.get("summary", "") or item.get("text", "")[:100]
    date = item.get("created_at", "")[:10]
    
    # Build URL based on source
    item_id = item.get("id", "")
    url = _build_url(source, username, item_id)
    
    lines.append(f"- **@{username}** ({date}): {summary}")
    if url:
        lines.append(f"  [View]({url})")
    lines.append("")
    
    return lines


def _build_url(source: str, username: str, item_id: str) -> str:
    """Build URL for an item based on source."""
    if source == "x" and item_id:
        return f"https://x.com/{username}/status/{item_id}"
    elif source == "instagram":
        return f"https://instagram.com/{username}"
    elif source == "tiktok":
        return f"https://tiktok.com/@{username}"
    elif source == "linkedin":
        return f"https://linkedin.com/in/{username}"
    elif source == "web":
        # Web items should have a URL in the item itself
        return ""
    return ""


# CLI entry point
if __name__ == "__main__":
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    filtered_file = Path("output/filtered.json")
    
    if not filtered_file.exists():
        logger.error(f"Filtered file not found: {filtered_file}")
        logger.error("Run filter.py first")
        exit(1)
    
    with open(filtered_file, "r") as f:
        filtered_data = json.load(f)
    
    generate_digest(filtered_data)

