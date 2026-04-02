import os

from langchain_community.chat_models import ChatOpenAI


def make_openrouter_chat_model(
    *,
    api_key: str | None = None,
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "openai/gpt-4o-mini",
) -> ChatOpenAI:
    key = api_key if api_key is not None else os.getenv("OPENROUTER_API_KEY")
    return ChatOpenAI(base_url=base_url, api_key=key, model=model)
