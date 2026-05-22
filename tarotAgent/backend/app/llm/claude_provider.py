import anthropic

from app.config import settings
from app.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.content[0].text

    async def stream_generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.7):
        async with self.client.messages.stream(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        ) as stream:
            async for text_stream_event in stream:
                if text_stream_event.type == "content_block_delta" and text_stream_event.delta.type == "text_delta":
                    yield text_stream_event.delta.text
