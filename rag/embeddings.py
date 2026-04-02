import os
from langchain_huggingface import HuggingFaceEmbeddings


def make_embeddings(
    *,
    model_name: str = "BAAI/bge-base-en",
    hf_token: str | None = None,
) -> HuggingFaceEmbeddings:
    token = hf_token if hf_token is not None else os.getenv("HF_TOKEN")
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"token": token},
    )
