from langchain_core.documents import Document


def build_constitution_rag_prompt(query: str, docs: list[Document]) -> str:
    context = "\n\n".join(
        [
            f"""
        Section {doc.metadata.get('section')} - {doc.metadata.get('title')}
        {doc.page_content}
        """
            for doc in docs
        ]
    )

    return f"""
You are a Nigerian legal assistant specializing in the 1999 Constitution.

Rules:
- Only answer using the provided context
- Do not make up laws
- If not found, say: 'I could not find this information in the Nigerian Constitution.'
- Always reference section numbers

Context:
{context}

Question:
{query}
"""
