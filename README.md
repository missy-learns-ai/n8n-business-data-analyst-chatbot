# n8n Business Data Analyst Chatbot

A chat-based business intelligence workflow built with **n8n**, **Supabase Postgres**, and a lightweight **Streamlit** user interface.

The original proof of concept connected an AI Agent directly to Google Sheets tools. Phase 1 is refactoring that prototype into a more reliable analytical foundation backed by structured planning, deterministic SQL calculations, validation, execution logging, and a separate UI layer.

> Phase 1 workflow export is still in progress. The current repository documents the target architecture and contracts; the finished n8n workflow export will be added once it is ready.

---

## Phase 1 Goal

Phase 1 turns the project from a demo chatbot into a trustworthy analytical workflow.

The core design rule is:

```text
The language model plans and explains.
Supabase SQL calculates.
Workflow nodes validate and enforce the process.
```

This matters because real business analytics should not rely on a language model to calculate numbers from raw rows. The model should interpret the user request and produce a structured plan. The workflow should validate that plan. The database should calculate the result. The response composer should explain only verified results.

---

## Application Layers

```text
Streamlit UI
-> n8n Webhook / Orchestrator Workflow
-> Supabase Postgres
-> n8n JSON response
-> Streamlit chat response
```

| Layer | Responsibility |
|---|---|
| Streamlit | User-facing chat UI. Sends user messages to n8n and renders the response. |
| n8n | Brain of the workflow: planning, validation, analytics routing, SQL execution, response generation and logging. |
| Supabase Postgres | Structured analytical data store and execution log store. |
| Model provider | Planner and response-composer language model calls inside n8n. |

The Streamlit UI does not connect directly to Supabase. It only calls the n8n webhook.

---

## Current Status

| Area | Status |
|---|---|
| Original prototype workflow | Present as `business-data-analyst-chatbot.json` |
| Phase 1 architecture documentation | In progress in `docs/architecture.md` |
| Planner prompt | Started in `prompts/orchestrator-planner.md` |
| Analysis-plan schema | Started in `schemas/analysis-plan.schema.json` |
| Metric registry contract | Started in `schemas/metric-registry.json` |
| Streamlit UI | Added in `streamlit_app/` |
| Supabase Postgres setup | Maintained outside the repo in Supabase/n8n credentials |
| Phase 1 workflow export | Pending upload when ready |
| Regression test set | Not started |

---

## Target Phase 1 Workflow

```text
Chat Trigger or Webhook Trigger
-> Prepare Input
-> Add Business Catalog
-> Planner Agent
-> Validate Analysis Plan
-> Main Switch
   -> ecommerce_orders analytics branch
   -> marketing_campaigns analytics branch
   -> clarification branch
   -> unsupported branch
   -> invalid_plan branch
-> Build Analytics Query / Controlled Response
-> Supabase Postgres deterministic query
-> Validate Analytics Result
-> Response Composer
-> Execution Log
-> Chat or Webhook Response
```

The workflow is intentionally kept as one orchestrator workflow during active Phase 1 development. The architecture separates responsibilities inside the workflow. If the canvas becomes difficult to maintain later, the branches can be split into importable sub-workflows.

See [docs/architecture.md](docs/architecture.md) for the detailed architecture baseline.

---

## Streamlit UI

The Streamlit app lives in:

```text
streamlit_app/
├── streamlit_app.py
├── requirements.txt
└── .streamlit/
    └── secrets.example.toml
```

Run locally:

```bash
cd streamlit_app
python -m pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
streamlit run streamlit_app.py
```

Set this secret locally or in Streamlit Community Cloud:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

For more details, see [streamlit_app/README.md](streamlit_app/README.md).

---

## Supported Phase 1 Data Domains

### Ecommerce Orders

Used for questions about:

- product categories
- products
- sales channels
- payment methods
- regions and countries
- order status and returns
- delivery days
- ratings
- gross sales, net sales, estimated profit and return rate

Example questions:

```text
Which product category has the highest sales?
Give me a breakdown of sales by product category.
How are PayPal orders distributed by gender?
Which region has the highest return rate?
```

### Marketing Campaigns

Used for questions about:

- campaign channels
- devices
- audience segments
- regions and countries
- spend
- impressions
- clicks
- conversions
- revenue
- ROAS, CTR, conversion rate and cost per conversion

Example questions:

```text
Which marketing channel has the highest ROAS?
Give me a breakdown of revenue by device.
Are mobile campaigns performing better than desktop campaigns?
Which campaigns have high spend but poor returns?
```

---

## Phase 1 Repository Structure

Target structure as the Phase 1 implementation matures:

```text
n8n-business-data-analyst-chatbot/
├── README.md
├── business-data-analyst-chatbot.json
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   └── operating-guide.md
├── workflows/
│   └── 01-reliable-analytics-foundation.json
├── prompts/
│   ├── orchestrator-planner.md
│   └── response-composer.md
├── schemas/
│   ├── analysis-plan.schema.json
│   ├── dataset-dictionary.json
│   ├── metric-registry.json
│   ├── analytics-result.schema.json
│   └── warnings.schema.json
├── evaluations/
│   └── phase1-golden-questions.csv
├── streamlit_app/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── README.md
└── sample-data/
```

Not every target file exists yet. Missing files are expected while Phase 1 is in progress.

---

## Important Security Notes

Do not commit secrets or private environment identifiers.

Never commit:

- OpenAI, Groq or other model-provider API keys
- Supabase database passwords
- raw Supabase connection strings
- n8n credential IDs from a private instance
- production webhook URLs if they are private
- OAuth access tokens or refresh tokens
- private Google Sheet URLs or private document IDs
- customer, employee or confidential company data

Use n8n credentials, Supabase settings, Streamlit secrets or environment variables for private values.

Safe placeholder examples:

```text
SUPABASE_HOST=YOUR_SUPABASE_HOST
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=YOUR_SUPABASE_USER
SUPABASE_PASSWORD=YOUR_SUPABASE_PASSWORD
N8N_WEBHOOK_URL=YOUR_N8N_WEBHOOK_URL
N8N_WEBHOOK_TOKEN=YOUR_OPTIONAL_TOKEN
```

---

## Phase 1 Acceptance Criteria

Phase 1 is complete when:

- the planner selects the correct dataset for at least 90% of Phase 1 test questions
- all numerical answers match trusted reference SQL calculations
- the workflow does not return an analytical answer when required data is unavailable
- every successful answer includes dataset name, record count, date period and warnings where relevant
- workflow JSON files and repository files contain no secrets or private credential values
- test questions are documented and repeatable
- repository documentation explains setup, architecture and limitations

---

## Original Prototype

The original workflow is still useful as a learning baseline. It demonstrates the basic conversational analytics experience:

```text
Start Conversation
-> AI Agent
-> Google Sheets Tool(s)
-> Edit Fields
-> Chat Response
```

Its main limitation is that the AI Agent handles planning, routing, retrieval, calculation and response generation all at once. Phase 1 separates those responsibilities so the project can become more testable and reliable.

---

## License

Add your preferred license here.

Common options:

- MIT License
- Apache License 2.0
- GPLv3
- No license / All rights reserved

---

## Disclaimer

This workflow is provided as a learning and demonstration template.

You are responsible for configuring your own n8n credentials, model-provider credentials, Supabase access, data permissions and security settings.

Do not use this workflow with sensitive, confidential, regulated or personally identifiable data unless your n8n instance, model provider, database and data-handling process meet your organization’s security and compliance requirements.
