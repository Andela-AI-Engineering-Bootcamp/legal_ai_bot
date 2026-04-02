from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def faiss_from_documents(documents: list[Document], embeddings: Embeddings) -> FAISS:
    return FAISS.from_documents(documents, embeddings)


def save_vectorstore(vectorstore: FAISS, path: str) -> None:
    vectorstore.save_local(path)


def load_vectorstore(
    path: str,
    embeddings: Embeddings,
    *,
    allow_dangerous_deserialization: bool = True,
) -> FAISS:
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=allow_dangerous_deserialization,
    )


def as_retriever(vectorstore: FAISS, *, search_type: str = "mmr", k: int = 5):
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k},
    )
