"""
Web/RSS Scraper - stub implementation.

Not yet implemented. Placeholder for future development.
Will support both RSS feeds and direct URL scraping.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseScraper

logger = logging.getLogger(__name__)


class WebScraper(BaseScraper):
    """Scraper for web content (RSS + URLs). NOT YET IMPLEMENTED."""
    
    SOURCE_NAME = "web"
    SOURCES_FILE = Path("sources/web/sources.json")
    
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """Load RSS feeds and URLs to scrape."""
        raise NotImplementedError(
            "Web scraper not yet implemented. "
            "To contribute, implement this method to load from sources/web/sources.json"
        )
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape content from RSS feeds and URLs."""
        raise NotImplementedError(
            "Web scraper not yet implemented. "
            "Requires RSS parsing (feedparser) and web scraping implementation."
        )
    
    def normalize_item(self, raw_item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize a raw web article/RSS entry."""
        raise NotImplementedError("Web scraper not yet implemented.")

