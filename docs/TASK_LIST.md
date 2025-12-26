# Task List: AI News Scraper

## Current Status: Phase 2 Complete ✅ — Ready for Phase 3

---

## ✅ Phase 1: Environment & Setup (COMPLETE)

- [x] Create `requirements.txt` 
- [x] Create `.gitignore`
- [x] Run `pip install -r requirements.txt`
- [x] Sign up for Apify account
- [x] Generate Apify API token
- [x] Create `.env` file with token

---

## ✅ seed_users.json (POPULATED)

58 users across 4 categories:
- **researchers:** 22 users
- **companies_labs:** 6 users  
- **influencers:** 19 users
- **practitioners:** 11 users

---

## ✅ Phase 2: Tweet Scraper (COMPLETE)

### Files Created:
| File | Purpose |
|------|---------|
| `seed_users.json` | List of 58 usernames (categorized) |
| `scrape_tweets.py` | Fetches tweets using Apify (FREE tier) |
| `raw_tweets.json` | Output file with scraped tweets |

### Last Run Results (Dec 23, 2025):
- **Users accessible:** ~35/58 (see Optional section for improvements)
- **Tweets fetched:** 57 (after 7-day filter)
- **Cost:** ~$0.10

### To Run:
```bash
python scrape_tweets.py
```

### Configuration (in scrape_tweets.py):
- `TWEETS_PER_USER = 20` — tweets fetched per user
- `BATCH_SIZE = 10` — users per API call
- `LOOKBACK_DAYS = 7` — only keep tweets from last N days

---

## 🔮 Phase 3: Filter (LLM Integration) - NOT STARTED

- [ ] Obtain Gemini or OpenAI API key
- [ ] Design and test classification prompts
- [ ] Build batching function for LLM calls
- [ ] Create `filter_tweets.py`

---

## 🤖 Phase 4: Automation - NOT STARTED

- [ ] Create `.github/workflows/weekly_digest.yaml`
- [ ] Store API keys in GitHub Secrets
- [ ] Configure output destination (email/Notion)

---

## 🔧 Optional: Improve Tweet Coverage (FUTURE)

Currently ~35/58 users are accessible via the free syndication endpoint. To improve coverage:

### Option A: Fix Username Typos
These usernames appear incorrect in `seed_users.json`:

| Current | Should Be |
|---------|-----------|
| `officialllogank` | `officiallogank` (one 'l') |
| `garymarkus` | `GaryMarcus` (capital M) |
| `deepmind` | `GoogleDeepMind` (rebranded) |

### Option B: Upgrade to Login-Based Scraper (~$10/month)
Would unlock access to 14 additional high-profile accounts:
- @ylecun, @drfeifei, @yoshuabengio, @gdb, @drjimfan
- @kdnuggets, @whats_ai, @svpino, @antgrasso
- @nigewillson, @arthurgretton, @reza_zadeh, @docmilanfar, @women_in_ai

**To implement:**
1. Rent `curious_coder/twitter-scraper` at https://console.apify.com/actors/74Alo9YdQrN
2. Update `ACTOR_ID` in `scrape_tweets.py`
3. Add Twitter login cookies to actor input

### Option C: Remove Inaccessible Users
Clean up `seed_users.json` to remove users that will never work:
- `_ganeshp`, `petitegeek`, `smolix`, `marcusborba`, `tessalau`

---

## 📁 Project Files Overview

```
ai-news-scraper/
├── .env                      # API tokens (git-ignored)
├── .gitignore
├── requirements.txt
├── seed_users.json           # 👈 YOU EDIT THIS
├── generate_reliable_profiles.py  # (Optional) Intersection scoring
├── scrape_tweets.py          # Phase 2: Tweet scraper
├── raw_tweets.json           # Output from scraper
├── PRD.md
├── IMPLEMENTATION_PLAN.md
└── TASK_LIST.md
```

---

## Notes
- Budget constraint: <$50 USD/month
- Tweet scraping: FREE (quacker/twitter-scraper)
- Weekly run schedule: Friday 09:00 UTC
- Target: 50-100 tracked profiles
