"""
Single place that decides which chat model/config to use — prompt.py,
routing, and the backend all just call get_llm() and don't care about
model specifics.
"""

import os
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.2):
    """
    Return the configured chat model. By default this talks straight to
    OpenAI; if CHAT_BASE_URL is set in .env, it points at that gateway
    instead (e.g. an OpenAI-compatible proxy) using CHAT_API_KEY for auth.
    Embeddings (ingestion/embed_store.py) are untouched — they always use
    OPENAI_API_KEY directly, since the gateway here doesn't support them.
    """
    model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    base_url = os.getenv("CHAT_BASE_URL")  # None -> real OpenAI, unchanged behavior
    api_key = os.getenv("CHAT_API_KEY") or os.getenv("OPENAI_API_KEY")

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
    )