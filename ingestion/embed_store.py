"""
Separated so "which embedding model" and "which vector DB" are decided in
exactly one place — everything else just calls build_vectorstore() or
get_vectorstore() and doesn't care how embeddings actually happen.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def _get_embeddings():
    model_name = "BAAI/bge-large-en-v1.5"
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )



def build_vectorstore(chunks, persist_dir: str = None):
    """
    Embed `chunks` with OpenAI embeddings and persist them to a Chroma
    vector store on disk. Run this once, offline, via run_ingestion.py.
    """
    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "vectorstore/chroma_db")
    embeddings = _get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vectorstore


def get_vectorstore(persist_dir: str = None):
    """
    Load an already-persisted Chroma store from disk (no re-embedding).
    This is what retrieval/retriever.py (Day 2) will call at request time —
    the backend never re-runs ingestion, it just opens the existing index.
    """
    persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "vectorstore/chroma_db")
    if not os.path.isdir(persist_dir):
        raise FileNotFoundError(
            f"No vector store found at '{persist_dir}'. "
            "Run `python -m ingestion.run_ingestion` first."
        )
    embeddings = _get_embeddings()
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)