"""
LinkedIn Scraper - stub implementation.

Not yet implemented. Placeholder for future development.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn content. NOT YET IMPLEMENTED."""
    
    SOURCE_NAME = "linkedin"
    ACCOUNTS_FILE = Path("sources/linkedin/accounts.json")
    
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """Load LinkedIn profiles and companies to scrape."""
        raise NotImplementedError(
            "LinkedIn scraper not yet implemented. "
            "To contribute, implement this method to load from sources/linkedin/accounts.json"
        )
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape posts from LinkedIn profiles and companies."""
        raise NotImplementedError(
            "LinkedIn scraper not yet implemented. "
            "Requires Apify actor selection and implementation."
        )
    
    def normalize_item(self, raw_item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize a raw LinkedIn post."""
        raise NotImplementedError("LinkedIn scraper not yet implemented.")

