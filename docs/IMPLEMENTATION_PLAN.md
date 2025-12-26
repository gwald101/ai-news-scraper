# Implementation Plan

## Phase 1: Environment & Discovery Logic (Days 1-2)
**Goal:** Generate the "Golden List" of ~50-100 accounts to track.
1.  **Setup:** Initialize Python project, install `apify-client`, `pandas`, `python-dotenv`.
2.  **Data Acquisition:** Use Apify to scrape the `following` list of the Seed Nodes. (Note: This is a heavy operation; run once).
3.  **Algorithm:** Implement the Intersection Scoring script (provided below) to rank users.
4.  **Review:** Manually audit the top 50 results to ensure quality. Save as `tracked_users.json`.

## Phase 2: The Scraper Pipeline (Days 3-4)
**Goal:** Get raw data from the Golden List.
1.  **Apify Actor Config:** Configure `apidojo/twitter-scraper-lite` to accept the handles from `tracked_users.json`.
2.  **Batching:** If the list > 50 users, split into batches to avoid timeout/rate limits.
3.  **Normalization:** Write a script to clean the JSON response (flatten nested quote-tweets, convert dates to UTC).

## Phase 3: The Filter (Day 5)
**Goal:** Turn noise into signal.
1.  **Prompt Engineering:** Test prompts with Gemini/OpenAI to reliably identify "News".
2.  **Integration:** Build a function that takes the raw JSON list, batches it (e.g., 20 tweets per LLM call), and returns structured summaries.

## Phase 4: Automation (Day 6)
**Goal:** "Set and Forget".
1.  **GitHub Actions:** Create a `.github/workflows/weekly_digest.yaml`.
2.  **Secrets:** Store Apify and LLM API keys in GitHub Secrets.
3.  **Output:** configure the script to email the result or append to a Notion page/Database.