# PRD: X.com AI News Aggregator & Discovery System

## 1. Problem Statement
Staying updated on AI research and industry moves via X.com is difficult due to high noise-to-signal ratios, algorithmic engagement farming, and restrictive API costs. Manual curation is time-consuming and prone to missing niche, high-value researchers.

## 2. Objective
Build an automated, cost-effective system to:
1.  **Discover** high-signal AI profiles through network analysis (Intersection Scoring).
2.  **Ingest** posts from these profiles on a weekly basis.
3.  **Filter** content using LLMs to extract legitimate news (papers, releases, hiring) vs. noise.

## 3. Core Features

### A. Discovery Module (One-off / Quarterly)
* **Input:** A "Seed List" of 5-10 trusted authorities (e.g., Karpathy, LeCun).
* ~~**Process:** Fetch the "Following" list of all Seed Nodes.~~ **[CANCELLED]** - Twitter requires login for following lists (June 2023 change). Auto-fetching not cost-effective.
* **Process (Manual):** Manually compile following lists from seed nodes into `seed_following.json`.
* **Logic:** Identify accounts followed by $\ge 2$ Seed Nodes (Intersection Scoring).
* **Filtering:** Apply keyword whitelisting to bios (e.g., "PhD", "Lab", "Building") to remove celebs/politicians.

### B. Ingestion Module (Weekly)
* **Tooling:** Apify (Twitter Scraper Lite or similar).
* **Schedule:** Runs every Friday at 09:00 UTC.
* **Volume:** Fetch last ~20 tweets per profile.
* **Data Points:** Tweet text, URL, Creation Date, Retweet Count, Quoted Tweet content.

### C. Intelligence Module (Processing)
* **Tooling:** LLM API (Gemini Flash 1.5 or GPT-4o-mini).
* **Prompt Logic:** Classify tweets into "News" vs. "Chatter". Summarize "News" into single-sentence bullets.
* **Output:** Markdown digest or JSON payload.

## 4. Non-Functional Requirements
* **Cost:** <$50 USD/month.
* **Latency:** Non-critical (Batch processing).
* **Reliability:** Must handle scraper failures/rate limits gracefully (retry logic).

## 5. Success Metrics
* **Relevance:** >90% of the final digest items are actual news (papers/releases).
* **Discovery:** System identifies at least 5 new relevant researchers per quarter.