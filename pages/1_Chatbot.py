from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from config import get_config, missing_required_values
from services.mongo_logger import log_chat_turn
from services.openai_client import generate_answer
from services.pdf_loader import build_context_text, load_documents


@st.cache_data(show_spinner=False)
def get_docs_cached(root_dir: str):
    return load_documents(Path(root_dir))


st.title("Chatbot")

config = get_config()
missing = missing_required_values(config)

docs, doc_errors = get_docs_cached(str(config.project_root))

for error in doc_errors:
    st.warning(f"PDF read error: {error}")

if not docs:
    st.error("No PDF files found in this folder. Add at least one `.pdf` file.")
    st.stop()

max_chars = st.sidebar.slider("Max context characters", min_value=2000, max_value=30000, value=10000, step=1000)
selected_doc_names = st.sidebar.multiselect(
    "Documents to use",
    options=[doc["name"] for doc in docs],
    default=[doc["name"] for doc in docs],
)

model = st.sidebar.text_input("Model", value=config.openai_model)

active_docs = [doc for doc in docs if doc["name"] in selected_doc_names]
if not active_docs:
    st.warning("Select at least one document in the sidebar.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Ask a question about your PDF(s)")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    if "OPENAI_API_KEY" in missing:
        answer = "OPENAI_API_KEY is missing. Add it to your .env file."
        latency_ms = 0
        status = "error"
        error_message = "missing_openai_api_key"
    else:
        context_text = build_context_text(active_docs, max_chars=max_chars)
        start = time.perf_counter()
        try:
            with st.spinner("Thinking..."):
                answer = generate_answer(
                    api_key=config.openai_api_key,
                    model=model,
                    user_query=user_query,
                    context_text=context_text,
                )
            status = "ok"
            error_message = None
        except Exception as exc:
            answer = f"OpenAI request failed: {exc}"
            status = "error"
            error_message = str(exc)
        latency_ms = int((time.perf_counter() - start) * 1000)

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    if config.mongodb_uri:
        try:
            log_chat_turn(
                uri=config.mongodb_uri,
                db_name=config.mongodb_db,
                collection_name=config.mongodb_collection,
                user_query=user_query,
                assistant_answer=answer,
                model=model,
                source_docs=[doc["name"] for doc in active_docs],
                latency_ms=latency_ms,
                status=status,
                error=error_message,
            )
        except Exception as exc:
            st.info(f"MongoDB logging skipped: {exc}")
    else:
        st.info("MONGODB_URI is missing. Chat works, but logs are not stored.")
