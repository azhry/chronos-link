"""LLM Factory — dynamic provider resolution.

Instantiates LangChain chat models based on the configured provider.
"""

from __future__ import annotations

from typing import Any
from chronos_link.config import settings


def get_llm(**kwargs: Any) -> Any:
    """Resolve and return the configured ChatModel.

    Supported providers: google, ollama, anthropic.
    """
    provider = settings.llm_provider.lower()
    model = settings.llm_model

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.gemini_api_key,
            **kwargs
        )
    
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            base_url=settings.ollama_base_url,
            **kwargs
        )
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            anthropic_api_key=settings.anthropic_api_key,
            **kwargs
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
