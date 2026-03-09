from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import get_config
from services.mongo_logger import fetch_recent_logs
from services.pdf_loader import load_documents


@st.cache_data(show_spinner=False)
def get_docs_cached(root_dir: str):
    return load_documents(Path(root_dir))


st.title("CMS - Document Viewer")

config = get_config()
docs, doc_errors = get_docs_cached(str(config.project_root))

if doc_errors:
    with st.expander("PDF read errors"):
        for error in doc_errors:
            st.write(f"- {error}")

if not docs:
    st.warning("No PDF files found in this folder.")
    st.stop()

doc_names = [doc["name"] for doc in docs]
selected_name = st.selectbox("Select document", options=doc_names)
selected_doc = next(doc for doc in docs if doc["name"] == selected_name)

col1, col2, col3 = st.columns(3)
col1.metric("Pages", selected_doc["page_count"])
col2.metric("Characters", selected_doc["char_count"])
col3.metric("Documents loaded", len(docs))

st.subheader("Excerpt")
st.text_area("Excerpt text", value=selected_doc["excerpt"], height=180)

st.subheader("Full extracted text")
st.text_area("Document text", value=selected_doc["text"], height=420)

st.divider()
st.subheader("Recent Chat Logs")
if config.mongodb_uri:
    try:
        logs = fetch_recent_logs(
            uri=config.mongodb_uri,
            db_name=config.mongodb_db,
            collection_name=config.mongodb_collection,
            limit=20,
        )
        if not logs:
            st.info("No logs found yet.")
        else:
            for log in logs:
                ts = log.get("timestamp")
                ts_display = str(ts) if ts else "unknown"
                with st.expander(f"{ts_display} - {log.get('status', 'unknown')}"):
                    st.write(f"**Question:** {log.get('user_query', '')}")
                    st.write(f"**Answer:** {log.get('assistant_answer', '')}")
                    st.write(f"**Model:** {log.get('model', '')}")
                    st.write(f"**Source Docs:** {', '.join(log.get('source_docs', []))}")
                    st.write(f"**Latency (ms):** {log.get('latency_ms', 0)}")
                    if log.get("error"):
                        st.write(f"**Error:** {log.get('error')}")
    except Exception as exc:
        st.error(f"Could not load MongoDB logs: {exc}")
else:
    st.info("MONGODB_URI is missing. Add it in `.env` to view logs.")
