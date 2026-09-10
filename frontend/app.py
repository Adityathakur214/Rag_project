"""
Zero LangChain / vector-store imports on purpose — the frontend only ever
talks to the FastAPI backend over HTTP and renders whatever JSON comes back.
"""

import os
import requests
import streamlit as st

def _get_backend_url() -> str:
    # Local runs read from .env (via os.getenv). Streamlit Community Cloud
    # runs read from the app's Secrets instead, exposed through st.secrets.
    try:
        return st.secrets["BACKEND_URL"]
    except Exception:
        return os.getenv("BACKEND_URL", "http://localhost:8000")


BACKEND_URL = _get_backend_url()

st.set_page_config(page_title="RAG Teaching Chat", page_icon="📚")
st.title("📚 RAG Teaching Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the conversation so far
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander("Sources"):
                for c in msg["citations"]:
                    st.markdown(f"- **{c['source']}**: {c['snippet']}")

question = st.chat_input("Ask something...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{BACKEND_URL}/ask", json={"question": question}, timeout=60)
                response.raise_for_status()
                data = response.json()
                answer = data.get("answer", "")
                citations = data.get("citations", [])
            except requests.RequestException as e:
                answer = f"Backend error: {e}"
                citations = []

        st.markdown(answer)
        if citations:
            with st.expander("Sources"):
                for c in citations:
                    st.markdown(f"- **{c['source']}**: {c['snippet']}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "citations": citations}
    )