"""
scaffold_project.py
Run this ONCE from the project root to (re)create the full folder/file
skeleton for the RAG project. Uses only the Python standard library, so it
works even before you've created a virtual environment or installed anything.

Usage (from the rag-project/ root folder):
    python scripts/scaffold_project.py

Safe to re-run: it will NOT overwrite a file that already has real content
in it (it only creates missing folders/files, or fills empty ones with a
TODO stub).
"""

import os

# Every folder that must exist. Order doesn't matter — os.makedirs handles it.
FOLDERS = [
    "data/raw",
    "ingestion",
    "retrieval",
    "routing",
    "generation",
    "backend",
    "frontend",
    "evaluation",
    "scripts",
    "vectorstore",  # where Chroma will persist its index files
]

# path -> one-line docstring stub explaining the file's job.
# If the file already exists AND is non-empty, scaffold leaves it alone.
FILES = {
    "ingestion/loader.py": '"""Loads raw documents from disk. """\n',
    "ingestion/splitter.py": '"""Splits documents into retrievable chunk. """\n',
    "ingestion/embed_store.py": '"""Embeds chunks and persists them to a Chroma vector store. """\n',
    "ingestion/run_ingestion.py": '"""One-shot offline pipeline: load -> split -> embed -> persist. """\n',
    "retrieval/retriever.py": '"""Wraps the persisted vector store as a LangChain retriever. """\n',
    "routing/query_router.py": '"""Classifies a query as general vs document before retrieval runs. """\n',
    "generation/prompt.py": '"""Prompt templates for the RAG path and the plain/general path. """\n',
    "generation/llm.py": '"""Returns the configured OpenAI chat model. TODO: Day 2."""\n',
    "generation/parser.py": '"""Pydantic answer schema + output parser (answer + citations). """\n',
    "backend/main.py": '"""FastAPI app: POST /ask wires router -> retrieval+generation or generation-only. """\n',
    "frontend/app.py": '"""Streamlit chat UI. Only calls the backend via requests.post(). """\n',
    "evaluation/testset.json": "[]\n",
    "evaluation/evaluate.py": '"""RAGAS scoring script over evaluation/testset.json. TODO: Day 4."""\n',
    "README.md": "# RAG Project\n\n — pipeline diagram + how to run + interview talking points.\n",
}

# __init__.py files so every folder is a proper importable package
INIT_FILES = ["ingestion", "retrieval", "routing", "generation", "backend", "frontend", "evaluation"]


def project_root():
    # scripts/ is one level below the project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_folders(root):
    for folder in FOLDERS:
        path = os.path.join(root, folder)
        os.makedirs(path, exist_ok=True)
        print(f"[folder] {folder}/")


def ensure_gitkeep(root):
    # keep the empty data/raw and vectorstore folders trackable in git
    for folder in ("data/raw", "vectorstore"):
        keep_path = os.path.join(root, folder, ".gitkeep")
        if not os.path.exists(keep_path):
            open(keep_path, "a").close()


def ensure_init_files(root):
    for folder in INIT_FILES:
        init_path = os.path.join(root, folder, "__init__.py")
        if not os.path.exists(init_path):
            open(init_path, "a").close()
            print(f"[file]   {folder}/__init__.py")


def ensure_files(root):
    for rel_path, stub_content in FILES.items():
        full_path = os.path.join(root, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            print(f"[skip]   {rel_path} (already has content)")
            continue
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(stub_content)
        print(f"[file]   {rel_path}")


def main():
    root = project_root()
    print(f"Scaffolding project at: {root}\n")
    ensure_folders(root)
    ensure_gitkeep(root)
    ensure_init_files(root)
    ensure_files(root)
    print("\nDone. Folder structure is ready.")


if __name__ == "__main__":
    main()