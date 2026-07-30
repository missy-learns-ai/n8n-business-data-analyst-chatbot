import os
import uuid
from typing import Any, Dict, Optional

import requests
import streamlit as st


APP_TITLE = "Business Data Analyst"
APP_SUBTITLE = "Ask ecommerce and marketing analytics questions. n8n handles the planning, SQL execution, validation, and response generation."


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read a value from Streamlit secrets first, then environment variables."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


def get_webhook_config() -> Dict[str, Optional[str]]:
    return {
        "url": get_secret("N8N_WEBHOOK_URL"),
        "token": get_secret("N8N_WEBHOOK_TOKEN"),
    }


def call_n8n(message: str, session_id: str) -> Dict[str, Any]:
    config = get_webhook_config()
    webhook_url = config["url"]

    if not webhook_url:
        return {
            "status": "configuration_error",
            "response": "N8N_WEBHOOK_URL is not configured. Add it in Streamlit secrets before using the app.",
            "warnings": ["Missing N8N_WEBHOOK_URL"],
        }

    headers = {"Content-Type": "application/json"}
    if config["token"]:
        headers["Authorization"] = f"Bearer {config['token']}"

    payload = {
        "session_id": session_id,
        "message": message,
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=90,
        )
        response.raise_for_status()
    except requests.Timeout:
        return {
            "status": "timeout",
            "response": "The analytics workflow took too long to respond. Please try again with a narrower question.",
            "warnings": ["n8n request timed out"],
        }
    except requests.RequestException as exc:
        return {
            "status": "request_error",
            "response": "I could not reach the n8n analytics workflow. Check the webhook URL and workflow status.",
            "warnings": [str(exc)],
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "status": "invalid_response",
            "response": response.text.strip() or "n8n returned an empty response.",
            "warnings": ["n8n did not return JSON"],
        }

    if isinstance(data, list) and data:
        data = data[0]

    if not isinstance(data, dict):
        return {
            "status": "invalid_response",
            "response": "n8n returned a response format this UI does not understand.",
            "warnings": ["Expected JSON object from n8n"],
        }

    if "response" not in data:
        data["response"] = data.get("message") or data.get("text") or "n8n returned JSON without a response field."

    return data


def init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"streamlit-{uuid.uuid4()}"
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_metadata(data: Dict[str, Any]) -> None:
    metadata_fields = {
        "Status": data.get("status"),
        "Dataset": data.get("dataset") or data.get("selected_dataset"),
        "Analysis type": data.get("analysis_type"),
        "Metric": data.get("metric") or data.get("metric_key"),
        "Record count": data.get("record_count") or data.get("row_count"),
        "Date start": data.get("date_start"),
        "Date end": data.get("date_end"),
    }
    metadata_fields = {key: value for key, value in metadata_fields.items() if value not in (None, "", [])}
    warnings = data.get("warnings") or []

    if not metadata_fields and not warnings:
        return

    with st.expander("Source and execution details", expanded=False):
        for key, value in metadata_fields.items():
            st.write(f"**{key}:** {value}")
        if warnings:
            st.write("**Warnings:**")
            for warning in warnings:
                st.write(f"- {warning}")


def render_examples() -> None:
    st.caption("Try one of these:")
    examples = [
        "Which product category has the highest sales?",
        "Give me a breakdown of sales by product category.",
        "Which marketing channel has the highest ROAS?",
        "Give me a breakdown of revenue by device.",
    ]
    for example in examples:
        st.code(example, language=None)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="BI", layout="centered")
    init_state()

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    with st.sidebar:
        st.header("Connection")
        config = get_webhook_config()
        st.write("n8n webhook:", "configured" if config["url"] else "missing")
        st.write("Webhook token:", "configured" if config["token"] else "not set")
        st.write("Session ID")
        st.code(st.session_state.session_id, language=None)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = f"streamlit-{uuid.uuid4()}"
            st.rerun()

    if not st.session_state.messages:
        render_examples()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("metadata"):
                render_metadata(message["metadata"])

    prompt = st.chat_input("Ask a business analytics question")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Running n8n analytics workflow...", expanded=False):
            data = call_n8n(prompt, st.session_state.session_id)
        answer = str(data.get("response", "No response returned."))
        st.markdown(answer)
        render_metadata(data)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": data,
    })


if __name__ == "__main__":
    main()
