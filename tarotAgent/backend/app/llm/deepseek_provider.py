from openai import AsyncOpenAI

from app.config import settings
from app.llm.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
