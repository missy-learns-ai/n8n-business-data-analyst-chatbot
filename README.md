# n8n Business Data Analyst Chatbot

A portfolio-ready business intelligence chatbot built with **n8n**, **Supabase Postgres**, and **Streamlit**.

The project started as a proof of concept where an AI Agent answered questions from a Google Sheet. Phase 1 refactors that prototype into a more reliable analytical system: the language model plans and explains, while Postgres performs the calculations and n8n enforces validation, routing, quality checks, and logging.

```text
The model plans and composes.
Postgres calculates.
n8n validates, routes, and logs.
Streamlit gives the workflow a clean user interface.
```

---

## What This Project Does

Users can ask natural-language questions about ecommerce orders and marketing campaigns, such as:

```text
Which product category has the highest sales?
Show net sales by sales channel.
Compare Electronics and Fashion by net sales.
Which channel has the highest ROAS?
Give me a breakdown of spend by channel last quarter.
Compare Instagram and TikTok by ROAS.
```

The workflow returns concise business answers with:

- verified metric values
- selected dataset
- record count
- date range
- warnings when data is unavailable or incomplete
- execution logs in Supabase

Unsupported or ambiguous questions fail cleanly before analytics SQL runs.

---

## Phase 1 Objective

**Reliable Analytical Foundation**

Refactor the existing demo into a modular and trustworthy analytics workflow while keeping a single n8n orchestrator. The workflow separates planning, validation, retrieval, calculation, data-quality validation, response composition, and execution logging.

Phase 1 is intentionally scoped to two datasets:

| Dataset | Purpose |
|---|---|
| `ecommerce_orders` | Ecommerce sales, orders, products, channels, geography, delivery, ratings, and returns |
| `marketing_campaigns` | Marketing spend, traffic, conversions, revenue, channels, devices, and campaign performance |

---

## Current Architecture

```text
Streamlit UI
-> n8n Webhook
-> Prepare Input
-> Business Catalog
-> Planner Agent
-> Planner Cache
-> Validate Analysis Plan
-> Resolve Date Range
-> Route by Dataset or Controlled Failure
-> Fetch Metric Definition from Supabase
-> Build Deterministic SQL
-> Execute Analytics Query in Postgres
-> Validate Analytics Result and Data Quality
-> Response Composer
-> Normalize Log Payload
-> Write Execution Log
-> Return Webhook Response
```

The n8n workflow is currently designed as one orchestrator workflow with clearly separated responsibility zones. This keeps Phase 1 easier to inspect and debug. A later phase can split these zones into separate reusable sub-workflows if the canvas becomes too large.

See [docs/architecture.md](docs/architecture.md) for the architecture baseline.

---

## Responsibility Split

| Component | Responsibility |
|---|---|
| Streamlit UI | Sends user questions to n8n and renders the final answer |
| Planner Agent | Classifies intent and extracts a structured analysis plan |
| Structured Output Parser | Enforces the required JSON shape from the planner |
| Validate Analysis Plan | Canonicalizes metrics/dimensions, applies routing rules, and blocks unsafe plans |
| Resolve Date Range | Converts relative periods such as last month and last quarter into explicit dates |
| Metric Registry | Stores approved KPI formulas and business definitions in Supabase |
| Build Analytics Query | Builds deterministic SQL from the validated plan and metric registry |
| Postgres Query Node | Executes the approved SQL against Supabase Postgres |
| Validate Analytics Result | Checks empty results, missing requested values, date coverage, and invalid metric output |
| Response Composer | Converts verified JSON into a short business answer without recalculating values |
| Execution Log | Stores traceability metadata for success and failure paths |

---

## Repository Structure

```text
n8n-business-data-analyst-chatbot/
├── README.md
├── business-data-analyst-chatbot.json
├── docs/
│   └── architecture.md
├── prompts/
│   └── orchestrator-planner.md
├── schemas/
│   ├── analysis-plan.schema.json
│   └── metric-registry.json
├── streamlit_app/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   ├── README.md
│   └── .streamlit/
│       ├── config.toml
│       └── secrets.example.toml
└── workflows/
    └── phase-1 workflow export pending
```

Some workflow and evaluation artifacts may still be added as the final n8n export and regression files are prepared.

---

## Streamlit UI

The Streamlit app is the user-facing layer. It does not connect directly to Supabase; it only calls the n8n webhook.

Current UI features:

- light theme for portfolio screenshots
- centered chat layout
- interactive sample questions
- clean processing state while n8n executes
- no visible Streamlit framework chrome
- no execution-details panel in the chat response
- environment-based webhook configuration

Run locally:

```bash
cd streamlit_app
python -m pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
streamlit run streamlit_app.py
```

Configure secrets in `.streamlit/secrets.toml`:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

For Streamlit-specific details, see [streamlit_app/README.md](streamlit_app/README.md).

---

## Streamlit Community Cloud Deployment

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from this repository.
4. Select the Phase 1 branch.
5. Set the app entrypoint to:

```text
streamlit_app/streamlit_app.py
```

6. Add these secrets in Streamlit Cloud:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

Do not commit `.streamlit/secrets.toml`.

---

## Supabase Tables

Phase 1 uses Supabase Postgres as the analytical and logging layer.

| Table | Purpose |
|---|---|
| `ecommerce_orders` | Ecommerce source dataset |
| `marketing_campaigns` | Marketing source dataset |
| `metric_registry` | Approved metric formulas and definitions |
| `analytics_execution_log` | Trace log for success, warning, failure, clarification, unsupported, and invalid-plan paths |
| `planner_cache` | Optional cache for unresolved structured plans |

Private connection strings and credentials are managed in Supabase, n8n credentials, or Streamlit secrets. They should not be committed to this repository.

---

## Phase 1 Metrics

### Ecommerce

| Metric | Meaning |
|---|---|
| `order_count` | Total ecommerce orders |
| `gross_sales` | Sales before discounts |
| `net_sales` | Sales after discounts |
| `return_rate` | Share of orders with returned status |
| `average_rating` | Average order rating |
| `average_delivery_days` | Average delivery duration |

### Marketing

| Metric | Meaning |
|---|---|
| `spend` | Total campaign spend |
| `impressions` | Total impressions |
| `clicks` | Total clicks |
| `conversions` | Total conversions |
| `revenue` | Total attributed revenue |
| `leads` | Total leads |
| `new_customers` | Total new customers |
| `ctr` | Click-through rate |
| `conversion_rate` | Share of clicks that became conversions |
| `cost_per_click` | Spend per click |
| `cost_per_conversion` | Spend per conversion |
| `roas` | Revenue per dollar of spend |
| `revenue_per_click` | Revenue per click |
| `lead_to_customer_rate` | Share of leads that became new customers |

---

## Response Contract

The Streamlit app expects n8n to return JSON with a user-facing `response` field.

Example:

```json
{
  "status": "success",
  "response": "The channel with the highest ROAS is TikTok, with a ROAS of 6.67.\nSource: marketing_campaigns · 1005 records · 2025-01-01 to 2026-06-30",
  "dataset": "marketing_campaigns",
  "metrics": ["roas"],
  "analysis_type": "grouped_metric_ranking",
  "row_count": 1005,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": []
}
```

Controlled failures should still return a `response` field so the UI can display a clean answer.

---

## Security Notes

Never commit secrets or private environment identifiers.

Do not commit:

- model-provider API keys
- Supabase database passwords
- raw Supabase connection strings
- n8n credential IDs
- private webhook URLs
- OAuth access tokens or refresh tokens
- private Google Sheet, Google Doc, or Supabase project URLs
- customer, employee, or confidential company data

Use placeholders in documentation and keep real values in n8n credentials, Supabase settings, Streamlit secrets, or environment variables.

---

## Phase 1 Acceptance Criteria

Phase 1 is complete when:

- the workflow selects the correct dataset for at least 90% of Phase 1 test questions
- all numerical answers match trusted SQL calculations
- no analytical answer is returned when required data is unavailable
- every answer includes source dataset, record count, date period, and warnings where relevant
- workflow JSON files contain no secrets or private credential values
- execution logging works across success and controlled-failure paths
- setup, architecture, workflow responsibilities, and limitations are documented

---

## Disclaimer

This project is a learning and portfolio implementation of an agentic analytics workflow.

Do not use it with sensitive, regulated, or confidential data unless your n8n instance, model provider, database, hosting environment, and data-handling process meet your security and compliance requirements.
