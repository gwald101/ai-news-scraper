"""
Intelligence Module: Filter content using LLM classification.

Classifies content from all sources as "News" vs "Chatter" using Gemini.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# --- PROMPT TEMPLATE ---

CLASSIFICATION_PROMPT = """You are an AI news curator. Analyze the following content items and classify each as either:
- "NEWS": Announcements of papers, product releases, funding, hiring, research breakthroughs, tool launches
- "CHATTER": Personal opinions, jokes, retweets without substance, engagement bait, general commentary

For each item classified as NEWS, provide a one-sentence summary.

Respond in JSON format:
```json
[
  {{
    "id": "item_id",
    "classification": "NEWS" or "CHATTER",
    "summary": "One sentence summary (only for NEWS, empty string for CHATTER)",
    "confidence": 0.0-1.0
  }}
]
```

CONTENT TO ANALYZE:
{content_json}

Respond ONLY with the JSON array, no other text."""


class ContentFilter:
    """LLM-based content classifier."""
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        """Initialize filter with configuration."""
        self.config = self._load_config(config_path)
        
        llm_config = self.config.get("llm", {})
        self.model_name = llm_config.get("model", "gemini-1.5-flash")
        self.batch_size = llm_config.get("batch_size", 10)
        
        general_config = self.config.get("general", {})
        self.output_dir = Path(general_config.get("output_dir", "output"))
        self.output_dir.mkdir(exist_ok=True)
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file."""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    
    def initialize(self) -> bool:
        """Initialize the LLM model. Returns True if successful."""
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.error("GEMINI_API_KEY not found or not set in .env")
            logger.error("Get your key at: https://aistudio.google.com/apikey")
            return False
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini model: {self.model_name}")
        return True
    
    def classify_batch(self, items: List[Dict]) -> List[Dict]:
        """
        Classify a batch of content items using the LLM.
        
        Args:
            items: List of content items with 'id', 'text', and optional metadata
            
        Returns:
            List of classification results
        """
        if not self.model:
            logger.error("Model not initialized. Call initialize() first.")
            return []
        
        # Prepare items for the prompt
        items_for_prompt = []
        for item in items:
            items_for_prompt.append({
                "id": item["id"],
                "source": item.get("source", "unknown"),
                "username": item.get("username", ""),
                "text": item.get("text", "")[:500],  # Truncate long content
                "urls": item.get("urls", [])[:2],
            })
        
        prompt = CLASSIFICATION_PROMPT.format(
            content_json=json.dumps(items_for_prompt, indent=2)
        )
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            results = json.loads(response_text)
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return []
    
    def filter(self, items: List[Dict], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Filter all content items and classify them.
        
        Args:
            items: List of content items to classify
            metadata: Optional metadata to include in output
            
        Returns:
            Dict with 'news' and 'chatter' lists, plus metadata
        """
        if not items:
            logger.warning("No items to filter")
            return {"news": [], "chatter": [], "metadata": metadata or {}}
        
        logger.info(f"Filtering {len(items)} items...")
        
        # Process in batches
        all_results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(items) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            results = self.classify_batch(batch)
            all_results.extend(results)
        
        # Merge results with original items
        results_by_id = {r["id"]: r for r in all_results}
        
        news_items = []
        chatter_items = []
        
        for item in items:
            item_id = item["id"]
            classification = results_by_id.get(item_id, {})
            
            item["classification"] = classification.get("classification", "UNKNOWN")
            item["summary"] = classification.get("summary", "")
            item["confidence"] = classification.get("confidence", 0)
            
            if item["classification"] == "NEWS":
                news_items.append(item)
            else:
                chatter_items.append(item)
        
        logger.info(f"Classification complete: {len(news_items)} NEWS, {len(chatter_items)} CHATTER")
        
        return {
            "news": news_items,
            "chatter": chatter_items,
            "metadata": {
                **(metadata or {}),
                "filtered_at": datetime.now(timezone.utc).isoformat(),
                "news_count": len(news_items),
                "chatter_count": len(chatter_items),
            }
        }
    
    def save_output(self, filtered_data: Dict) -> Path:
        """Save filtered results to JSON file."""
        output_file = self.output_dir / "filtered.json"
        
        with open(output_file, "w") as f:
            json.dump(filtered_data, f, indent=2)
        
        logger.info(f"Saved filtered results to {output_file}")
        return output_file


def load_combined_content(output_dir: Path = Path("output")) -> Optional[Dict]:
    """
    Load combined content from aggregate output.
    
    Falls back to legacy raw_tweets.json if combined_raw.json doesn't exist.
    """
    combined_file = output_dir / "combined_raw.json"
    legacy_file = Path("raw_tweets.json")
    
    # Try combined file first
    if combined_file.exists():
        with open(combined_file, "r") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data.get('items', []))} items from {combined_file}")
        return data
    
    # Fall back to legacy file
    if legacy_file.exists():
        with open(legacy_file, "r") as f:
            data = json.load(f)
        
        # Convert legacy format
        tweets = data.get("tweets", [])
        for tweet in tweets:
            tweet["source"] = "x"  # Add source field
        
        logger.info(f"Loaded {len(tweets)} items from legacy {legacy_file}")
        return {
            "items": tweets,
            "metadata": data.get("metadata", {}),
        }
    
    logger.error("No content files found. Run scrapers first.")
    return None


# CLI entry point
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    from .digest import generate_digest
    
    logger.info("=" * 60)
    logger.info("Content Filter - Intelligence Module")
    logger.info("=" * 60)
    
    # Load content
    data = load_combined_content()
    if not data:
        exit(1)
    
    items = data.get("items", [])
    metadata = data.get("metadata", {})
    
    # Initialize and run filter
    filter_obj = ContentFilter()
    if not filter_obj.initialize():
        exit(1)
    
    filtered = filter_obj.filter(items, metadata)
    filter_obj.save_output(filtered)
    
    # Generate digest
    digest_path = generate_digest(filtered)
    logger.info(f"Generated digest at {digest_path}")

