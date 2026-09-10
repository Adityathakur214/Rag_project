"""
Separated so "which embedding model" and "which vector DB" are decided in
exactly one place — everything else just calls build_vectorstore() or
get_vectorstore() and doesn't care how embeddings actually happen.
"""

import os
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma


_embeddings = None  # cached after first load, reused for every later request


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        api_key = os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError(
                "HF_TOKEN is not set. Create a free 'Read' token at "
                "https://huggingface.co/settings/tokens and add it to .env "
                "(and to Render's Environment settings)."
            )
        _embeddings = HuggingFaceEndpointEmbeddings(
            model=model,
            task="feature-extraction",
            huggingfacehub_api_token=api_key,
        )
    return _embeddings


def build_vectorstore(chunks, persist_dir: str = None):
    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "vectorstore/chroma_db")
    embeddings = _get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vectorstore


def get_vectorstore(persist_dir: str = None):
    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "vectorstore/chroma_db")
    if not os.path.isdir(persist_dir):
        raise FileNotFoundError(
            f"No vector store found at '{persist_dir}'. "
            "Run `python -m ingestion.run_ingestion` first."
        )
    embeddings = _get_embeddings()
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)