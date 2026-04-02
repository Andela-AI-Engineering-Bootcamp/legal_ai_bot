from collections.abc import Callable

from langchain_core.documents import Document

from rag.prompts import build_constitution_rag_prompt


def rag_query(
    query: str,
    *,
    retriever,
    llm,
    build_prompt: Callable[[str, list[Document]], str] | None = None,
) -> str:
    builder = build_prompt or build_constitution_rag_prompt
    docs = retriever.invoke(query)
    prompt = builder(query, docs)
    response = llm.invoke(prompt)
    return response.content
