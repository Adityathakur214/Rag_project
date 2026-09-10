"""
Two templates: one for document-grounded answers (retrieved context +
citation instructions), one for plain general chat. routing/query_router.py
decides which one gets used per request.
"""

from langchain_core.prompts import ChatPromptTemplate
from generation.parser import answer_parser

_FORMAT_INSTRUCTIONS = answer_parser.get_format_instructions()

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant that answers ONLY using the provided "
     "context. If the context doesn't contain the answer, say so honestly "
     "instead of guessing. Always cite the source document(s) you used.\n\n"
     "{format_instructions}"),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
]).partial(format_instructions=_FORMAT_INSTRUCTIONS)

GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly assistant having plain conversation — no document "
     "context is available for this message, so just answer normally and "
     "leave the citations list empty.\n\n{format_instructions}"),
    ("human", "{question}"),
]).partial(format_instructions=_FORMAT_INSTRUCTIONS)