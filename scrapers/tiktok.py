"""
TikTok Scraper - stub implementation.

Not yet implemented. Placeholder for future development.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseScraper

logger = logging.getLogger(__name__)


class TikTokScraper(BaseScraper):
    """Scraper for TikTok content. NOT YET IMPLEMENTED."""
    
    SOURCE_NAME = "tiktok"
    ACCOUNTS_FILE = Path("sources/tiktok/accounts.json")
    
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """Load TikTok accounts to scrape."""
        raise NotImplementedError(
            "TikTok scraper not yet implemented. "
            "To contribute, implement this method to load from sources/tiktok/accounts.json"
        )
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape videos from TikTok accounts."""
        raise NotImplementedError(
            "TikTok scraper not yet implemented. "
            "Requires Apify actor selection and implementation."
        )
    
    def normalize_item(self, raw_item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize a raw TikTok video."""
        raise NotImplementedError("TikTok scraper not yet implemented.")

