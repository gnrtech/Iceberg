# Job Aggregation System

Python-based, modular job aggregation pipeline to fetch real-time openings from
company career portals in India using API-first extraction where possible.

## Features

- Detects portal type: **Workday**, **Greenhouse**, **Lever**, or **Custom HTML**
- Uses provider-specific extractors (API-first strategy)
- Handles Workday pagination
- Normalizes output fields:
  - job title
  - company name
  - location
  - job URL
- Applies keyword + location filters
- Deduplicates jobs by URL
- Returns top N jobs in a social-shareable text format
- Exposes extraction reports for observability and future automation

## Input format

Use a JSON file with:

```json
{
  "companies": [
    {"name": "Accenture", "url": "https://accenture.wd3.myworkdayjobs.com/accenturecareers"},
    {"name": "Wipro", "url": "https://wipro.wd3.myworkdayjobs.com/WiproCareers"},
    {"name": "Infosys", "url": "https://careers.infosys.com"},
    {"name": "TCS", "url": "https://www.tcs.com/careers"}
  ],
  "keywords": ["data engineer", "python", "spark", "azure", "etl"],
  "locations": ["india", "bangalore", "hyderabad", "pune", "chennai", "gurgaon", "remote"],
  "limit": 15
}
```

A sample is included at `example_input.json`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Formatted output:

```bash
python -m job_aggregator.cli --input-json example_input.json --top 15
```

JSON output:

```bash
python -m job_aggregator.cli --input-json example_input.json --json-output
```

## Output example

```text
🔥 Data Engineer Jobs (India) – 2026-04-03

👉 Data Engineer – Accenture
📍 Bangalore, India
🔗 https://accenture.wd3.myworkdayjobs.com/job/123
```

## Architecture

- `job_aggregator/detector.py`: portal detection
- `job_aggregator/providers/*.py`: provider-specific connectors
- `job_aggregator/filters.py`: keyword/location filters + dedupe + limit
- `job_aggregator/aggregator.py`: orchestration pipeline
- `job_aggregator/formatter.py`: final text renderer
- `job_aggregator/cli.py`: command-line entrypoint

## Scale to 100+ companies

- Add more providers (SmartRecruiters, Taleo, etc.)
- Move company list into DB/config service
- Add async workers and rate-limit controls
- Cache responses to reduce portal load
- Persist normalized postings for trend analytics

## Daily automation integration

The output text from `format_jobs_text` is ready to:

- Post to X/Twitter via API client
- Push to WhatsApp (Business API / Twilio)
- Send via Slack, Telegram, or email digest

Run the CLI daily via cron/GitHub Actions/Airflow and publish output downstream.