# n8n Business Data Analyst Chatbot

A business intelligence chatbot built with **n8n**, **Supabase Postgres**, and **Streamlit**. The project lets users ask natural-language questions about ecommerce and marketing performance. n8n handles the agentic workflow, Postgres performs deterministic calculations, and Streamlit provides a clean chat interface.
Streamlit: https://data-analytics-bi-chatbot.streamlit.app/
```text
The model plans and explains.
Postgres calculates the numbers.
n8n validates, routes, and logs the workflow.
Streamlit gives the system a user-facing chat UI.
```
<img width="1390" height="611" alt="image" src="https://github.com/user-attachments/assets/7f3b2371-1967-4662-8c5e-98c1365df064" />

---

## What It Can Answer

<img width="1439" height="858" alt="image" src="https://github.com/user-attachments/assets/850d020e-238c-411f-a619-52289d918ed8" />

Example questions:

```text
Which product category has the highest sales?
Show net sales by sales channel.
What are net sales for Electronics?
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
- warnings when data is missing or incomplete
- execution logs in Supabase

Unsupported or ambiguous questions fail cleanly before analytics SQL runs.

---

## Architecture

```text
Streamlit UI
-> n8n Webhook
-> Prepare Input
-> Business Catalog
-> Planner Agent
-> Planner Cache
-> Validate Analysis Plan
-> Resolve Date Range
-> Dataset Router
-> Fetch Metric Definition
-> Build Deterministic SQL
-> Execute Postgres Query
-> Validate Analytics Result
-> Response Composer
-> Execution Log
-> Webhook Response
```

The workflow is intentionally structured as one n8n orchestrator with clear responsibility zones. This keeps the system easy to inspect while still separating planning, validation, calculation, data-quality checks, response generation, and logging.

See [docs/architecture.md](docs/architecture.md) for more implementation detail.

---

## Repository Structure

```text
n8n-business-data-analyst-chatbot/
├── README.md
├── database/
│   └── schema.sql
├── docs/
│   ├── architecture.md
│   ├── database-setup.md
│   └── assets/
├── knowledge/
│   ├── metric-dictionary.md
│   ├── dataset-dictionary.md
│   ├── policies/
│   ├── playbooks/
│   └── sample-reports/
├── prompts/
│   └── orchestrator-planner.md
├── sample-data/
│   └── business-data-analyst-sample-datasets.zip
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
    ├── business-data-analyst-chatbot.workflow.json
    └── prototype-business-data-analyst-googlesheets.workflow.json
```

The importable n8n workflow is available at:

[workflows/business-data-analyst-chatbot.workflow.json](workflows/business-data-analyst-chatbot.workflow.json)

The earlier Google Sheets proof-of-concept workflow is preserved as:

[workflows/prototype-business-data-analyst-googlesheets.workflow.json](workflows/prototype-business-data-analyst-googlesheets.workflow.json)

---

## Supported Data Domains

### Ecommerce Orders

Used for sales, orders, products, channels, geography, delivery, ratings, and returns.

Supported metrics:

| Metric | Meaning |
|---|---|
| `order_count` | Total ecommerce orders |
| `gross_sales` | Sales before discounts |
| `net_sales` | Sales after discounts |
| `return_rate` | Share of orders with returned status |
| `average_rating` | Average order rating |
| `average_delivery_days` | Average delivery duration |

Supported dimensions include product category, product name, sales channel, payment method, order status, region, country, city, gender, and age group.

### Marketing Campaigns

Used for campaign spend, traffic, conversions, revenue, channels, devices, audience segments, and campaign performance.

Supported metrics:

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

Supported dimensions include channel, region, country, audience segment, device, campaign objective, and campaign status.

---

## n8n Workflow Setup

1. Import [workflows/business-data-analyst-chatbot.workflow.json](workflows/business-data-analyst-chatbot.workflow.json) into n8n.
2. Reconnect the model credential on the planner and response-composer model nodes.
3. Reconnect the Postgres credential on all Supabase/Postgres nodes.
4. Confirm the webhook path and production webhook URL.
5. Run test questions from the Streamlit app or n8n webhook.

The workflow JSON does not include private credential values. You must reconnect your own n8n credentials after import.

---

## Supabase Tables

The workflow expects these Postgres tables:

| Table | Purpose |
|---|---|
| `ecommerce_orders` | Ecommerce source dataset |
| `marketing_campaigns` | Marketing source dataset |
| `metric_registry` | Approved KPI formulas and business definitions |
| `analytics_execution_log` | Trace log for success and controlled-failure paths |
| `planner_cache` | Optional cache for reusable structured plans |

Keep database passwords and connection strings in Supabase and n8n credentials, not in repository files.

See [docs/database-setup.md](docs/database-setup.md) and [database/schema.sql](database/schema.sql) for the table contract and setup SQL.

---

## Knowledge Corpus

The repository includes a retrieval-ready knowledge corpus in [knowledge/](knowledge/). It defines the metric dictionary, dataset dictionary, grounding policies, analysis playbooks, and sample reports that can support a future RAG layer.

The corpus is designed to complement deterministic analytics:

- Postgres remains responsible for calculating numbers.
- n8n remains responsible for routing, validation, logging, and workflow control.
- Retrieved knowledge can support definitions, interpretation, policy checks, and recommendations.

---

## Streamlit UI

The Streamlit app is the user-facing layer. It only calls the n8n webhook and does not connect directly to Supabase.
<img width="1439" height="817" alt="image" src="https://github.com/user-attachments/assets/f1c49ba5-915d-481c-bec2-222d03a9871a" />

Current UI features:

- light theme
- centered chat layout
- interactive sample questions
- clean processing state while n8n executes
- hidden Streamlit framework chrome
- environment-based webhook configuration

Run locally:

```bash
cd streamlit_app
python -m pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
streamlit run streamlit_app.py
```

Configure `.streamlit/secrets.toml`:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

For more detail, see [streamlit_app/README.md](streamlit_app/README.md).

---

## Streamlit Community Cloud Deployment

1. Create a new app from this GitHub repository.
2. Set the main file path to:

```text
streamlit_app/streamlit_app.py
```

3. Add secrets in Streamlit Cloud:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

Do not commit `.streamlit/secrets.toml`.

---

## Response Contract

The Streamlit app expects n8n to return JSON with a user-facing `response` field.

Example:

```json
{
  "status": "success",
  "response": "The channel with the highest ROAS is TikTok, with a ROAS of 6.67.\nSource: marketing_campaigns | 1005 records | 2025-01-01 to 2026-06-30",
  "dataset": "marketing_campaigns",
  "metrics": ["roas"],
  "analysis_type": "grouped_metric_ranking",
  "row_count": 1005,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": []
}
```

Controlled failures should still return a `response` field so the UI can display a clear answer.

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

## Disclaimer

This project is a learning and portfolio implementation of an agentic analytics workflow.

Do not use it with sensitive, regulated, or confidential data unless your n8n instance, model provider, database, hosting environment, and data-handling process meet your security and compliance requirements.
