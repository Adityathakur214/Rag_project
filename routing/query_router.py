"""
Kept separate from retrieval and generation so the general-vs-document
decision is its own testable module — swap or improve the classifier later
without touching retrieval or generation code.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    "system",
     "You are a strict query classifier for a RAG system with an internal "
     "knowledge base. Reply with exactly one word: 'general' or 'document'.\n\n"
     "- 'general' = ONLY pure greetings, small talk, or meta questions about "
     "the assistant itself (e.g. 'hi', 'thanks', 'what can you do').\n"
     "- 'document' = ANY substantive, factual, or technical question — even "
     "if you personally already know the answer. Default to 'document' "
     "whenever there is any chance the knowledge base has relevant "
     "information.\n\n"
     "Reply with only the single word, nothing else.",
    ("human", "{query}"),
    
])


# Built lazily (on first real call) so this module can be imported before
# .env is loaded, without crashing on a missing OPENAI_API_KEY at import time.
_router_chain = None


def _get_router_chain():
    global _router_chain
    if _router_chain is None:
        model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        base_url = os.getenv("CHAT_BASE_URL")
        api_key = os.getenv("CHAT_API_KEY") or os.getenv("OPENAI_API_KEY")
        # temperature=0 -> deterministic classification, not creative writing
        llm = ChatOpenAI(model=model, temperature=0, base_url=base_url, api_key=api_key)
        _router_chain = ROUTER_PROMPT | llm | StrOutputParser()
    return _router_chain


def classify_query(query: str) -> str:
    """
    Classify a query as "general" (skip the vector store) or "document"
    (needs retrieval). Falls back to "document" on any unexpected model
    output, since an unnecessary vector-store hit is cheaper than silently
    missing context the user actually needed.
    """
    raw = _get_router_chain().invoke({"query": query}).strip().lower()
    return "general" if "general" in raw else "document"


if __name__ == "__main__":
    # Quick manual check: python -m routing.query_router
    from dotenv import load_dotenv

    load_dotenv()
    for test_query in [
        "hi, how are you?",
        "what does the uploaded PDF say about the refund policy?",
    ]:
        print(f"{test_query!r} -> {classify_query(test_query)}")