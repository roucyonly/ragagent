from abc import ABC, abstractmethod

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        ...


def get_provider() -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "deepseek":
        from app.llm.deepseek_provider import DeepSeekProvider
        return DeepSeekProvider()
    elif provider_name == "openai":
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "claude":
        from app.llm.claude_provider import ClaudeProvider
        return ClaudeProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
