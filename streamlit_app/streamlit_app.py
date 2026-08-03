import os
import uuid
from typing import Any, Dict, Optional

import requests
import streamlit as st


APP_TITLE = "Ask Your Business Data"
APP_SUBTITLE = (
    "Get trusted ecommerce and marketing answers through an agentic analytics "
    "workflow powered by n8n and Postgres."
)


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


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          #MainMenu,
          footer,
          header,
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          [data-testid="stStatusWidget"] {
            display: none;
          }

          .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 5rem;
          }

          .hero-header {
            margin-bottom: 0.35rem;
          }

          .hero-title {
            margin: 0;
            color: rgb(31, 35, 48);
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 760;
            line-height: 1.05;
          }

          .app-subtitle {
            color: rgba(49, 51, 63, 0.72);
            max-width: 620px;
            margin-bottom: 1.1rem;
            line-height: 1.45;
          }

          .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid rgba(24, 128, 80, 0.22);
            border-radius: 999px;
            padding: 0.32rem 0.62rem;
            margin-top: 0.3rem;
            background: rgba(24, 128, 80, 0.08);
            color: rgb(17, 102, 65);
            font-size: 0.86rem;
            font-weight: 600;
            white-space: nowrap;
            width: fit-content;
          }

          .status-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            background: rgb(24, 128, 80);
            box-shadow: 0 0 0 0.18rem rgba(24, 128, 80, 0.12);
          }

          div[data-testid="stButton"] > button {
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 8px;
            padding: 0.72rem 0.8rem;
            color: rgba(49, 51, 63, 0.82);
            background: rgba(250, 250, 250, 0.72);
            font-size: 0.92rem;
            text-align: left;
            justify-content: flex-start;
            transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
          }

          div[data-testid="stButton"] > button:hover {
            border-color: rgba(33, 96, 179, 0.38);
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            transform: translateY(-1px);
            color: rgb(23, 78, 156);
            background: rgba(33, 96, 179, 0.06);
          }

          div[data-testid="stButton"] > button:focus,
          div[data-testid="stButton"] > button:active {
            border-color: rgba(24, 128, 80, 0.48);
            color: rgb(17, 102, 65);
            background: rgba(24, 128, 80, 0.08);
            box-shadow: 0 0 0 0.16rem rgba(24, 128, 80, 0.12);
          }

          div[data-testid="stChatInput"] {
            border-color: rgba(24, 128, 80, 0.32);
          }

          div[data-testid="stChatInput"]:focus-within {
            border-color: rgba(24, 128, 80, 0.68);
            box-shadow: 0 0 0 0.16rem rgba(24, 128, 80, 0.12);
          }

          div[data-testid="stChatInput"] button,
          div[data-testid="stChatInput"] button:hover,
          div[data-testid="stChatInput"] button:focus,
          div[data-testid="stChatInput"] button:active {
            color: rgb(17, 102, 65);
            background: transparent;
            border-color: transparent;
            box-shadow: none;
          }

          div[data-testid="stChatInput"] button svg {
            fill: rgb(17, 102, 65);
            color: rgb(17, 102, 65);
          }

          .welcome-bubble {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
            margin: 0.65rem 0 1rem;
            background: rgba(250, 250, 250, 0.82);
            color: rgba(31, 35, 48, 0.86);
            line-height: 1.45;
          }

          .thinking-bubble {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 8px;
            padding: 0.7rem 0.85rem;
            background: rgba(250, 250, 250, 0.75);
            color: rgba(49, 51, 63, 0.78);
            font-size: 0.95rem;
          }

          .typing-dots {
            display: inline-flex;
            gap: 0.22rem;
          }

          .typing-dots span {
            width: 0.36rem;
            height: 0.36rem;
            border-radius: 999px;
            background: rgba(49, 51, 63, 0.5);
            animation: typing-bounce 1.15s infinite ease-in-out;
          }

          .typing-dots span:nth-child(2) {
            animation-delay: 0.16s;
          }

          .typing-dots span:nth-child(3) {
            animation-delay: 0.32s;
          }

          @keyframes typing-bounce {
            0%, 80%, 100% {
              transform: translateY(0);
              opacity: 0.45;
            }
            40% {
              transform: translateY(-0.18rem);
              opacity: 1;
            }
          }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_examples() -> Optional[str]:
    examples = [
        "Which product category has the highest sales?",
        "Give me a breakdown of spend by channel last quarter.",
        "Compare Instagram and TikTok by ROAS.",
        "Can you analyze employee salaries?",
    ]
    st.caption("Start with a sample question")

    selected_prompt = None
    for row_start in range(0, len(examples), 2):
        columns = st.columns(2)
        for column, example in zip(columns, examples[row_start:row_start + 2]):
            with column:
                if st.button(example, key=f"example_{row_start}_{example}", use_container_width=True):
                    selected_prompt = example

    return selected_prompt


def render_thinking() -> None:
    st.markdown(
        """
        <div class="thinking-bubble">
          <span>Analyzing your question</span>
          <span class="typing-dots"><span></span><span></span><span></span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome() -> None:
    st.markdown(
        """
        <div class="welcome-bubble">
          Hi, I am connected to the analytics workflow. What would you like to analyze?
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="BI", layout="centered")
    init_state()
    inject_styles()

    st.markdown(
        """
        <div class="hero-header">
          <h1 class="hero-title">Ask Your Business Data</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='app-subtitle'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='status-pill'><span class='status-dot'></span>n8n Agent Ready</div>",
        unsafe_allow_html=True,
    )

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

    intro_placeholder = st.empty()
    selected_example = None
    if not st.session_state.messages:
        with intro_placeholder.container():
            render_welcome()
            selected_example = render_examples()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_prompt = st.chat_input("Ask about sales, ROAS, products, or channels...")
    prompt = selected_example or typed_prompt

    if not prompt:
        return

    intro_placeholder.empty()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with response_placeholder.container():
            render_thinking()

        data = call_n8n(prompt, st.session_state.session_id)
        answer = str(data.get("response", "No response returned."))

        response_placeholder.empty()
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": data,
    })


if __name__ == "__main__":
    main()
