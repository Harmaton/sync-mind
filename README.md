# sync-mind

## Problem

Retail traders and investment portfolio advisors often struggle to make use of the vast amounts of market data, financial news, and trading signals available to them.
Analyzing this information in a timely and effective manner is challenging without the right tools.

Sync-Mind solves this by ingesting market data from the Polygon API via Airbyte into MongoDB, merging it with user-generated trades and journal entries.
MindsDB then uses this combined dataset to train and expose ML engines (price forecasting, Google Gemini, and Langchain-based models) as an AI-driven advisor accessible through Slack.
This allows users to forecast prices, record trades, and request data-driven investment advice or analysis—all without leaving their Slack workspace.

## Demo Video

Watch a quick demo of Sync-Mind in action:

[![Demo Video]](https://www.loom.com/share/e79782b86dfa4aaea0f903c878b50320?sid=2c26a49b-845a-475c-8f14-38e1b057c8f8)


## Command Prefixes

The prefixes you can use when you @-mention the bot (or reply in thread) to pick exactly which feature fires:

### Forecasting
- `forecast`
- `predict`

**Note:** Date is required for forecasting. Please specify the date in the format `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`.

**Example:**
```text
@SyncMind forecast AAPL price 2025-05-28
@SyncMind predict BTC/USD 2025-05-28T12:00
```

### Advice / Analysis (Langchain)
- `advice`
- `analysis`
- `recommend`
- `advisor`

**Example:**
```text
@SyncMind advice Should I add more AAPL to my portfolio?
@SyncMind analysis What’s your take on the tariffs hike?
```

## Run Locally

- Ensure you have [uvicorn](https://www.uvicorn.org/) installed:
   ```bash
   pip install uvicorn
   ```
1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp server/.env.example server/.env
   ```
2. Install Python dependencies:
   ```bash
   pip install -r server/requirements.txt
   ```
3. Launch with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```
4. In another terminal, expose your app to Slack via ngrok:
   ```bash
   ngrok http 8080
   ```
