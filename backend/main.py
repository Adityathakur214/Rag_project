"""
Only routing/wiring lives here. All RAG logic (routing decision, retrieval,
prompt, model, structured parsing) is imported from routing/, retrieval/,
and generation/ — this file just plugs them together behind one endpoint.
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

from routing.query_router import classify_query
from retrieval.retriever import get_retriever
from generation.llm import get_llm
from generation.prompt import RAG_PROMPT, GENERAL_PROMPT
from generation.parser import answer_parser, AnswerSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up embeddings + vectorstore at startup itself, so the first
    # real user query never has to wait for the HF model download.
    get_retriever()
    yield


app = FastAPI(title="RAG Teaching API", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str


def _format_context(docs) -> str:
    # Plain formatting glue, not RAG logic — just turns retrieved Documents
    # into the {context} string the RAG prompt expects, tagged with source
    # so the model (and the parser's citations) can point back to them.
    return "\n\n".join(
        f"[source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerSchema)
def ask(request: AskRequest):
    question = request.question
    route = classify_query(question)
    llm = get_llm()

    if route == "document":
        retriever = get_retriever()
        docs = retriever.invoke(question)
        context = _format_context(docs)
        chain = RAG_PROMPT | llm | answer_parser
        return chain.invoke({"context": context, "question": question})

    chain = GENERAL_PROMPT | llm | answer_parser
    return chain.invoke({"question": question})