"""
Standalone offline script: load -> split -> embed -> persist.
Run this once whenever your source documents change. The backend NEVER
imports this file — at request time it only reads the already-persisted
vector store (see ingestion/embed_store.get_vectorstore in Day 2's retriever.py).

Run from the project root (as a module, so the `ingestion` package imports
resolve correctly):
    python -m ingestion.run_ingestion
"""

import os
from dotenv import load_dotenv

from ingestion.loader import load_documents
from ingestion.splitter import split_into_chunks
from ingestion.embed_store import build_vectorstore


def main():
    load_dotenv()

    data_dir = os.getenv("DATA_DIR", "data/raw")
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "vectorstore/chroma_db")

    print(f"[1/3] Loading documents from '{data_dir}'...")
    documents = load_documents(data_dir)
    print(f"      Loaded {len(documents)} document(s).")

    print("[2/3] Splitting into chunks...")
    chunks = split_into_chunks(documents)
    print(f"      Created {len(chunks)} chunk(s).")

    print(f"[3/3] Embedding chunks and persisting to '{persist_dir}'...")
    build_vectorstore(chunks, persist_dir=persist_dir)
    print("      Done.")

    print(f"\nVector store ready at '{persist_dir}'. You can now build retrieval on top of it.")


if __name__ == "__main__":
    main()