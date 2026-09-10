"""
Defines the structured shape every answer must return — separated so
prompt.py can inject format instructions and the backend can validate the
model's output without duplicating the schema anywhere else.
"""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


class Citation(BaseModel):
    source: str = Field(description="The document path/filename the answer relied on")
    snippet: str = Field(description="A short quote or paraphrase from that source supporting the answer")


class AnswerSchema(BaseModel):
    answer: str = Field(description="The final answer to the user's question")
    citations: List[Citation] = Field(
        default_factory=list,
        description="Sources used to produce the answer. Empty list for general/non-document answers.",
    )


# One shared parser instance — both the RAG prompt and the general prompt
# (generation/prompt.py) inject its format instructions, so every answer
# comes back in the exact same shape regardless of which path handled it.
answer_parser = PydanticOutputParser(pydantic_object=AnswerSchema)