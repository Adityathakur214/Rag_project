"""
Separated from splitting/embedding so "how do I get documents in" can be
swapped (folder, single file, future URL loader) without touching anything
downstream.
"""

import os
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
)

# Map file extensions to the LangChain loader class that knows how to read them.
LOADER_MAPPING = {
    ".txt": TextLoader,
    ".md": TextLoader,
    ".pdf": PyPDFLoader,
}


def load_documents(source: str):
    """
    Load every supported file under `source` (a folder path) and return a
    list of LangChain Document objects.

    Each Document keeps its own `metadata["source"]` (the file path) — this
    is what later becomes the citation shown to students in the final answer.
    """
    if not os.path.isdir(source):
        raise ValueError(f"'{source}' is not a folder. Point DATA_DIR at a folder of files.")

    all_docs = []
    for ext, loader_cls in LOADER_MAPPING.items():
        loader = DirectoryLoader(
            source,
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            show_progress=False,
        )
        docs = loader.load()
        all_docs.extend(docs)

    if not all_docs:
        raise ValueError(
            f"No supported files (.txt, .md, .pdf) found in '{source}'. "
            "Drop some source documents in there first."
        )

    return all_docs


if __name__ == "__main__":
    # Quick manual check: python ingestion/loader.py
    from dotenv import load_dotenv

    load_dotenv()
    data_dir = os.getenv("DATA_DIR", "data/raw")
    documents = load_documents(data_dir)
    print(f"Loaded {len(documents)} document(s) from '{data_dir}':")
    for doc in documents:
        print(f"  - {doc.metadata.get('source')}")