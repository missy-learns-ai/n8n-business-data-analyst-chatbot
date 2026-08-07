# Agentic Business Intelligence Chatbot

A production-inspired business intelligence chatbot built with n8n, Supabase Postgres, and Streamlit.

The system lets users ask natural-language questions about ecommerce and marketing performance, then routes each question through a controlled analytics workflow instead of relying on the AI model to calculate answers directly.

To reduce the black-box nature of AI, the language model is used only for planning and response composition. It classifies the user’s intent, selects the dataset, metric, dimension, filters, and date range, then returns a structured analysis plan. n8n validates that plan against approved business rules before any database query runs.

All numerical answers are calculated deterministically in Supabase Postgres using approved metric definitions from a metric registry. The workflow also performs data-quality validation, handles unsupported or ambiguous questions with controlled responses, and logs each execution with trace ID, dataset, metrics, row count, date range, warnings, and status.

To reduce latency and token cost, repeatable planning outputs are cached, business logic is moved out of prompts where possible, and the model is kept away from raw-row calculations. This makes the assistant more reliable, auditable, and closer to how AI analytics workflows need to behave in real business environments.

Streamlit demo: https://data-analytics-bi-chatbot.streamlit.app/

```text
Core design:
- The model plans and explains.
- Postgres calculates the numbers.
- n8n validates, routes, caches, and logs the workflow.
- Streamlit provides the user-facing chat interface.
```
<img width="1395" height="562" alt="image" src="https://github.com/user-attachments/assets/a41a4879-4707-4d3f-a5d2-292e580f37ff" />

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
-> Request Guard
-> Prepare Input
-> Business Catalog
-> Planner / Cache
-> Validate Analysis Plan
-> Resolve Date Range
-> Fetch Dataset Metadata
-> Metadata Authorization Guard
-> Fetch Metric Definition
-> Build Analytics Query
-> SQL Safety Guard
-> Execute Postgres Query
-> Validate Analytics Result
-> Response Composer
-> Response Safety Guard
-> Format Final Response
-> Webhook Response
-> Execution Log
```

The workflow is intentionally structured as one n8n orchestrator with clear responsibility zones. This keeps the system easy to inspect while still separating request protection, planning, validation, metadata authorization, calculation, data-quality checks, response generation, response safety, and logging.

### Metadata-Driven Refactor

The analytics execution layer was refactored from separate ecommerce and marketing query-builder branches into a more generic metadata-driven pattern.

Earlier versions duplicated the same SQL-building logic for each dataset. The current workflow fetches approved dataset metadata and metric definitions from Supabase, then uses those trusted definitions to build deterministic SQL.

This makes the system easier to extend:

- dataset rules live in metadata instead of scattered workflow code
- metric formulas come from `metric_registry`
- cache-hit and cache-miss paths go through the same validation layer
- adding a dataset requires metadata and metric definitions, not copied workflow branches
- empty or unsafe execution paths return controlled responses instead of blank webhook responses

### Layered Guardrails

The workflow uses layered guardrails so the LLM can plan and explain, but cannot directly control execution.

```text
Webhook
-> Request Guard
-> Planner / Cache
-> Validate Analysis Plan
-> Metadata Authorization Guard
-> Build Analytics Query
-> SQL Safety Guard
-> Execute Analytics Query
-> Validate Analytics Result
-> Response Composer
-> Response Safety Guard
-> Execution Log
```

| Guardrail | Placement | Purpose |
|---|---|---|
| Request Guard | Immediately after Webhook | Validates request shape, detects PII, prompt injection, secret extraction, and unsafe database intent before planner execution. |
| Cache Revalidation | Cache hit path before date resolution | Treats cached plans as untrusted and revalidates them through the same `Validate Analysis Plan` node as new planner outputs. |
| Validate Analysis Plan | After Planner Agent or cached plan restore | Normalizes planner output, applies aliases, validates dataset, metric, dimension, filters, date column, limit, and analysis type. |
| Metadata Authorization Guard | After dataset metadata and metric definition lookup | Confirms the selected dataset, metric, dimensions, filters, table name, and date column are approved before SQL generation. |
| SQL Safety Guard | Between Build Analytics Query and Execute Analytics Query | Allows only read-only `SELECT` / `WITH` analytics queries and blocks destructive or multi-statement SQL patterns. |
| Validate Analytics Result | After Postgres execution | Checks empty results, missing values, invalid comparison values, null metric values, incomplete date ranges, warnings, and controlled failure cases. |
| Response Safety Guard | After Response Composer | Checks final user-facing text for empty responses, missing source details, internal implementation details, secrets, and unsafe claims. |
| Execution Log | Final logging path | Stores trace ID, question, selected dataset, metrics, analysis type, row count, date range, warnings, status, and timestamp. |

Security design principles:

- User input is untrusted.
- Planner output is untrusted.
- Cached plans are untrusted.
- Metadata-driven context must be authorized before use.
- SQL is generated only from approved metadata and metric definitions.
- Postgres performs deterministic calculations.
- The LLM does not calculate metrics or execute SQL directly.
- Security warnings are logged internally.
- Data-quality warnings may be shown to users when helpful.

Failure routing:

| Failure type | Route / status | User behavior |
|---|---|---|
| Prompt injection, PII, secret extraction, unsafe database intent | `security_blocked` | Controlled safety refusal |
| Out-of-scope but harmless request | `unsupported` | Scope explanation with suggested analytics topics |
| Ambiguous analytics request | `clarification` | One clarification question |
| Invalid planner output | `invalid_plan` | Safe failure message |
| Empty or incomplete analytics result | `failed` or `success_with_warnings` | Controlled response with data-quality warning |

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
3. Reconnect read-only Supabase/Postgres credentials on metadata, metric, and analytics query nodes.
4. Reconnect audit/write Supabase/Postgres credentials on planner cache and execution log nodes.
5. Confirm the webhook path and production webhook URL.
6. Run test questions from the Streamlit app or n8n webhook.

The workflow JSON does not include private credential values. You must reconnect your own n8n credentials after import.

---

## Supabase Tables

The workflow expects these Postgres tables:

| Table | Purpose |
|---|---|
| `ecommerce_orders` | Ecommerce source dataset |
| `marketing_campaigns` | Marketing source dataset |
| `dataset_metadata` | Approved dataset tables, dimensions, aliases, date columns, and supported analysis types |
| `metric_registry` | Approved KPI formulas and business definitions |
| `analytics_execution_log` | Trace log for success and controlled-failure paths |
| `planner_cache` | Optional cache for reusable structured plans |

Keep database passwords and connection strings in Supabase and n8n credentials, not in repository files.

See [docs/database-setup.md](docs/database-setup.md) and [database/schema.sql](database/schema.sql) for the table contract and setup SQL.

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
