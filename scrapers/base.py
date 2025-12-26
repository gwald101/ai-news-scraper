"""
Base scraper class - abstract interface for all source scrapers.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all content scrapers.
    
    Each source (X, Instagram, TikTok, etc.) should implement this interface.
    """
    
    # Override in subclasses
    SOURCE_NAME: str = "base"
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        """Initialize scraper with configuration."""
        self.config = self._load_config(config_path)
        self.general_config = self.config.get("general", {})
        self.source_config = self.config.get("sources", {}).get(self.SOURCE_NAME, {})
        
        self.lookback_days = self.general_config.get("lookback_days", 7)
        self.output_dir = Path(self.general_config.get("output_dir", "output"))
        self.output_dir.mkdir(exist_ok=True)
        
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file."""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    
    def is_enabled(self) -> bool:
        """Check if this source is enabled in config."""
        return self.source_config.get("enabled", False)
    
    @abstractmethod
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """
        Load accounts/users to scrape from source-specific config file.
        
        Returns:
            Dict with categories as keys and lists of accounts as values,
            or None if loading fails.
        """
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape content from the source.
        
        Returns:
            List of normalized content items.
        """
        pass
    
    @abstractmethod
    def normalize_item(self, raw_item: Dict) -> Optional[Dict[str, Any]]:
        """
        Normalize a raw item to a consistent format.
        
        Args:
            raw_item: Raw data from the scraper
            
        Returns:
            Normalized item dict, or None if item should be filtered out.
        """
        pass
    
    def save_output(self, items: List[Dict], metadata: Dict) -> Path:
        """
        Save scraped items to JSON file.
        
        Args:
            items: List of normalized items
            metadata: Metadata about the scrape
            
        Returns:
            Path to the output file
        """
        output_file = self.output_dir / f"{self.SOURCE_NAME}_raw.json"
        
        output = {
            "source": self.SOURCE_NAME,
            "metadata": {
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "date_range": {
                    "from": self.cutoff_date.isoformat(),
                    "to": datetime.now(timezone.utc).isoformat(),
                    "lookback_days": self.lookback_days,
                },
                **metadata,
            },
            "items": items,
        }
        
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Output saved to {output_file}")
        return output_file
    
    def run(self) -> Optional[Path]:
        """
        Run the full scrape pipeline.
        
        Returns:
            Path to output file, or None if scraping failed/disabled.
        """
        if not self.is_enabled():
            logger.info(f"{self.SOURCE_NAME} scraper is disabled in config")
            return None
        
        logger.info("=" * 60)
        logger.info(f"{self.SOURCE_NAME.upper()} Scraper")
        logger.info("=" * 60)
        
        items = self.scrape()
        
        if not items:
            logger.warning(f"No items scraped from {self.SOURCE_NAME}")
            return None
        
        metadata = {
            "total_items": len(items),
        }
        
        return self.save_output(items, metadata)

