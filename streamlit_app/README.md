# Streamlit UI

This folder contains a lightweight Streamlit chat interface for the Phase 1 business analyst workflow.

Streamlit is the face of the project. n8n remains the brain.

```text
Streamlit UI
-> n8n Webhook
-> Planner / validation / Supabase Postgres analytics
-> n8n JSON response
-> Streamlit chat response
```

## Files

```text
streamlit_app/
├── streamlit_app.py
├── requirements.txt
└── .streamlit/
    └── secrets.example.toml
```

## n8n Webhook Contract

The app sends a POST request to n8n:

```json
{
  "session_id": "streamlit-generated-session-id",
  "message": "Which product category has the highest sales?"
}
```

The n8n workflow should return JSON with at least:

```json
{
  "status": "success",
  "response": "The product category with the highest net sales is Electronics...",
  "dataset": "ecommerce_orders",
  "record_count": 1005,
  "date_start": "2025-01-01",
  "date_end": "2026-06-30",
  "warnings": []
}
```

The UI also understands optional fields such as `analysis_type`, `metric`, `metric_key`, `selected_dataset`, and `row_count`.

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

Edit `.streamlit/secrets.toml` with your n8n webhook URL.

Run the app:

```bash
streamlit run streamlit_app.py
```

## Deploy From GitHub

Use Streamlit Community Cloud:

1. Go to `https://share.streamlit.io`.
2. Create a new app from GitHub.
3. Select this repository.
4. Select the Phase 1 branch.
5. Set the entrypoint to:

```text
streamlit_app/streamlit_app.py
```

6. In advanced settings, add secrets:

```toml
N8N_WEBHOOK_URL = "https://YOUR_N8N_DOMAIN/webhook/business-analyst-chat"
N8N_WEBHOOK_TOKEN = ""
```

Do not commit `.streamlit/secrets.toml`.

## Notes

- Streamlit should not connect directly to Supabase for Phase 1.
- Supabase credentials stay inside n8n/Supabase configuration.
- Streamlit only calls the n8n webhook and displays the returned answer.
- Use the n8n production webhook only after the workflow is saved and active.
