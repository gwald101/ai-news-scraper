"""
Instagram Scraper - stub implementation.

Not yet implemented. Placeholder for future development.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseScraper

logger = logging.getLogger(__name__)


class InstagramScraper(BaseScraper):
    """Scraper for Instagram content. NOT YET IMPLEMENTED."""
    
    SOURCE_NAME = "instagram"
    ACCOUNTS_FILE = Path("sources/instagram/accounts.json")
    
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """Load Instagram accounts to scrape."""
        raise NotImplementedError(
            "Instagram scraper not yet implemented. "
            "To contribute, implement this method to load from sources/instagram/accounts.json"
        )
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape posts from Instagram accounts."""
        raise NotImplementedError(
            "Instagram scraper not yet implemented. "
            "Requires Apify actor selection and implementation."
        )
    
    def normalize_item(self, raw_item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize a raw Instagram post."""
        raise NotImplementedError("Instagram scraper not yet implemented.")

