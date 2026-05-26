from openai import AsyncOpenAI
from modules.ai.providers.base import BaseAIProvider
from shared.schemas import AIResponse
from config.settings import settings
import json

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = "gpt-4o-mini"

    async def generate_text(self, prompt: str, system_prompt: str = None, model: str = None) -> AIResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=0.7
        )

        return AIResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=model or self.default_model,
            raw_response=None
        )

    async def extract_structured_data(self, prompt: str, schema: dict, system_prompt: str = None, model: str = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": f"{prompt}\n\nReturn JSON following this schema: {json.dumps(schema)}"})

        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
