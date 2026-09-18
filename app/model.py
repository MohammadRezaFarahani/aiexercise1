from langchain_openai import ChatOpenAI

from app.config import (
    CUSTOM_API_KEY,
    CUSTOM_BASE_URL,
    CUSTOM_MODEL,
)


model = ChatOpenAI(
    model=CUSTOM_MODEL,
    api_key=CUSTOM_API_KEY,
    base_url=CUSTOM_BASE_URL,
    timeout=60,
    max_retries=2,
)