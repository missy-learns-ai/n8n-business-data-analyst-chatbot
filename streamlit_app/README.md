# Streamlit UI

This folder contains the Streamlit interface for the Phase 1 business analyst chatbot.

Streamlit is the face of the project. n8n remains the analytics brain.

```text
User
-> Streamlit chat UI
-> n8n webhook
-> planner, validation, metric registry, Postgres analytics, response composition
-> Streamlit answer
```

---

## Current UI Behavior

The app is designed as a clean portfolio-facing chat experience:

- light theme
- centered content column
- hidden Streamlit header/menu/footer artifacts
- `n8n Agent Ready` status indicator
- short welcome message
- interactive sample questions
- chat input that remains available after sample-question clicks
- temporary `Analyzing your question` state while n8n runs
- final answer rendered as normal chat text
- no source-details expander in the UI

The source, record count, date range, and warnings should be included in the response text returned by n8n.

---

## Files

```text
streamlit_app/
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .streamlit/
    ├── config.toml
    └── secrets.example.toml
```

`config.toml` sets the app to a light theme and keeps the toolbar minimal.

---

## Local Setup

Install dependencies:

```bash
cd streamlit_app
python -m pip install -r requirements.txt
```

Create local secrets:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

Run the app:

```bash
streamlit run streamlit_app.py
```

---

## n8n Webhook Request

The app sends a POST request to n8n:

```json
{
  "session_id": "streamlit-generated-session-id",
  "message": "Which product category has the highest sales?"
}
```

If `N8N_WEBHOOK_TOKEN` is configured, the app sends it as a bearer token:

```text
Authorization: Bearer <token>
```

---

## n8n Webhook Response

The app expects n8n to return either a JSON object or a one-item JSON array.

Minimum expected response:

```json
{
  "status": "success",
  "response": "The product category with the highest sales is Electronics, with net sales of $29,296.07.\nSource: ecommerce_orders · 1005 records · 2025-01-01 to 2026-06-30"
}
```

Recommended response fields:

```json
{
  "status": "success",
  "response": "Final user-facing answer",
  "dataset": "ecommerce_orders",
  "metrics": ["net_sales"],
  "analysis_type": "grouped_metric_ranking",
  "row_count": 1005,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": []
}
```

Controlled failures should also return a user-facing `response` field:

```json
{
  "status": "unsupported",
  "response": "I can help with ecommerce orders and marketing campaign analytics. This question looks outside the datasets currently available in Phase 1.",
  "warnings": ["Unsupported dataset or question type."]
}
```

---

## Deploy From GitHub

Use Streamlit Community Cloud:

1. Open Streamlit Community Cloud.
2. Create a new app from GitHub.
3. Select this repository and the Phase 1 branch.
4. Set the main file path to:

```text
streamlit_app/streamlit_app.py
```

5. Add secrets in Streamlit Cloud:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

Do not commit `.streamlit/secrets.toml`.

---

## Notes

- Streamlit should not connect directly to Supabase in Phase 1.
- Supabase credentials stay in n8n/Supabase configuration.
- The n8n workflow should return final text that already includes source, row count, date range, and warnings.
- Use the n8n production webhook only after the workflow is active.
