"""
Separated so chunking strategy (size/overlap/splitter type) can change
without touching how documents are loaded or how they get embedded.
"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_into_chunks(docs, chunk_size: int = None, chunk_overlap: int = None):
    """
    Split loaded Documents into smaller chunks sized for retrieval.

    chunk_size / chunk_overlap fall back to .env values (CHUNK_SIZE,
    CHUNK_OVERLAP) so the whole class can tune them from one place.
    """
    chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", 1000))
    chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", 150))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    return chunks


if __name__ == "__main__":
    # Quick manual check: python -m ingestion.splitter
    from dotenv import load_dotenv
    from ingestion.loader import load_documents

    load_dotenv()
    data_dir = os.getenv("DATA_DIR", "data/raw")
    documents = load_documents(data_dir)
    chunks = split_into_chunks(documents)
    print(f"{len(documents)} document(s) -> {len(chunks)} chunk(s)")
    if chunks:
        print("\nFirst chunk preview:")
        print(chunks[0].page_content[:300])