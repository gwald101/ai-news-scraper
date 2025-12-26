"""
X (Twitter) Scraper - fetches tweets from tracked users.

Uses the Apify quacker/twitter-scraper actor (FREE tier).
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv

from .base import BaseScraper

load_dotenv()

logger = logging.getLogger(__name__)


class XScraper(BaseScraper):
    """Scraper for X (Twitter) content."""
    
    SOURCE_NAME = "x"
    USERS_FILE = Path("sources/x/users.json")
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        super().__init__(config_path)
        
        self.api_token = os.getenv("APIFY_API_TOKEN")
        self.actor_id = self.source_config.get("actor_id", "quacker/twitter-scraper")
        self.tweets_per_user = self.source_config.get("tweets_per_user", 20)
        self.batch_size = self.source_config.get("batch_size", 10)
        self.timeout_secs = self.source_config.get("timeout_secs", 300)
        
        self.categorized_users: Optional[Dict[str, List[str]]] = None
    
    def load_accounts(self) -> Optional[Dict[str, List[str]]]:
        """Load Twitter usernames from sources/x/users.json."""
        if not self.USERS_FILE.exists():
            logger.error(f"File not found: {self.USERS_FILE}")
            return None
        
        try:
            with open(self.USERS_FILE, "r") as f:
                data = json.load(f)
            
            # Handle flat list format
            if isinstance(data, list):
                users = [u.lower().replace("@", "").strip() for u in data if u]
                logger.info(f"Loaded {len(users)} users from {self.USERS_FILE}")
                return {"uncategorized": users}
            
            # Handle categorized format
            if isinstance(data, dict):
                categorized = {}
                total = 0
                for category, users in data.items():
                    if category.startswith("_"):  # Skip metadata fields
                        continue
                    if isinstance(users, list):
                        normalized = [u.lower().replace("@", "").strip() for u in users if u]
                        categorized[category] = normalized
                        total += len(normalized)
                        logger.info(f"  {category}: {len(normalized)} users")
                
                logger.info(f"Loaded {total} users across {len(categorized)} categories")
                return categorized
            
            logger.error("Invalid format in users.json")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.USERS_FILE}: {e}")
            return None
    
    def _flatten_users(self, categorized: Dict[str, List[str]]) -> List[str]:
        """Flatten categorized users into a single list."""
        all_users = []
        for users in categorized.values():
            all_users.extend(users)
        return list(set(all_users))
    
    def _scrape_batch(self, client: ApifyClient, handles: List[str]) -> List[Dict]:
        """Scrape tweets for a batch of users."""
        logger.info(f"Scraping tweets for {len(handles)} users: {', '.join(handles[:5])}{'...' if len(handles) > 5 else ''}")
        
        try:
            run = client.actor(self.actor_id).call(
                run_input={
                    "handles": handles,
                    "tweetsDesired": self.tweets_per_user,
                    "proxyConfig": {"useApifyProxy": True},
                },
                timeout_secs=self.timeout_secs
            )
            
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            logger.info(f"Retrieved {len(items)} tweets")
            return items
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
    
    def normalize_item(self, raw_tweet: Dict) -> Optional[Dict[str, Any]]:
        """Normalize a raw tweet to a consistent format."""
        tweet_id = raw_tweet.get("id_str") or raw_tweet.get("id") or ""
        
        # Parse creation date
        created_at_raw = raw_tweet.get("created_at", "")
        created_at = None
        created_at_iso = created_at_raw
        
        try:
            created_at = datetime.strptime(created_at_raw, "%a %b %d %H:%M:%S %z %Y")
            created_at_iso = created_at.isoformat()
        except (ValueError, TypeError):
            pass
        
        # Filter by date
        if created_at and created_at < self.cutoff_date:
            return None
        
        # Extract user info
        user_data = raw_tweet.get("user", {})
        username = user_data.get("screen_name") or raw_tweet.get("username", "unknown")
        
        # Get tweet text
        text = (
            raw_tweet.get("full_text") or 
            raw_tweet.get("text") or 
            raw_tweet.get("tweet_text") or 
            ""
        )
        
        # Extract URLs
        urls = []
        entities = raw_tweet.get("entities", {})
        for url_obj in entities.get("urls", []):
            expanded = url_obj.get("expanded_url") or url_obj.get("url")
            if expanded:
                urls.append(expanded)
        
        # Handle quoted tweets
        quoted_tweet = raw_tweet.get("quoted_status") or raw_tweet.get("quoted_tweet")
        quoted_text = ""
        if quoted_tweet:
            quoted_text = quoted_tweet.get("full_text") or quoted_tweet.get("text", "")
        
        # Determine category
        category = "unknown"
        if self.categorized_users:
            for cat, users in self.categorized_users.items():
                if username.lower() in users:
                    category = cat
                    break
        
        return {
            "id": str(tweet_id),
            "source": self.SOURCE_NAME,
            "username": username.lower(),
            "category": category,
            "created_at": created_at_iso,
            "text": text,
            "urls": urls,
            "retweet_count": raw_tweet.get("retweet_count", 0),
            "favorite_count": raw_tweet.get("favorite_count", 0),
            "is_retweet": text.startswith("RT @") or raw_tweet.get("retweeted", False),
            "quoted_text": quoted_text,
        }
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape tweets from all tracked users."""
        if not self.api_token:
            logger.error("APIFY_API_TOKEN not found in environment")
            return []
        
        self.categorized_users = self.load_accounts()
        if not self.categorized_users:
            return []
        
        users = self._flatten_users(self.categorized_users)
        logger.info(f"Total unique users to scrape: {len(users)}")
        logger.info(f"Filtering tweets from: {self.cutoff_date.strftime('%Y-%m-%d')} to now")
        
        client = ApifyClient(self.api_token)
        all_items = []
        filtered_count = 0
        
        for i in range(0, len(users), self.batch_size):
            batch = users[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(users) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            raw_tweets = self._scrape_batch(client, batch)
            
            for raw in raw_tweets:
                normalized = self.normalize_item(raw)
                if normalized:
                    all_items.append(normalized)
                else:
                    filtered_count += 1
        
        logger.info(f"Filtered out {filtered_count} tweets older than {self.lookback_days} days")
        
        # Sort by date (newest first)
        all_items.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        
        return all_items
    
    def run(self) -> Optional[Path]:
        """Run the full scrape pipeline with X-specific metadata."""
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
        
        users_with_items = len(set(t["username"] for t in items))
        
        metadata = {
            "total_items": len(items),
            "users_requested": len(self._flatten_users(self.categorized_users)) if self.categorized_users else 0,
            "users_with_items": users_with_items,
            "categories": {cat: len(users) for cat, users in (self.categorized_users or {}).items()},
        }
        
        return self.save_output(items, metadata)


# CLI entry point for standalone execution
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    scraper = XScraper()
    scraper.run()

