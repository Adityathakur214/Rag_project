"""
Separated so "how many chunks to retrieve" / "which persisted store to use"
lives in one place — routing and generation just call get_retriever() and
don't care about vector-store internals.
"""

import os
from ingestion.embed_store import get_vectorstore


def get_retriever(k: int = None):
    """
    Return a LangChain retriever wrapping the already-persisted Chroma
    vector store. Does NOT re-embed anything — ingestion must already have
    been run once via `python -m ingestion.run_ingestion`.
    """
    k = k or int(os.getenv("RETRIEVER_K", 4))
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})