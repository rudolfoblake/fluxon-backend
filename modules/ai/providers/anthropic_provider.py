from anthropic import AsyncAnthropic
from modules.ai.providers.base import BaseAIProvider
from shared.schemas import AIResponse
from config.settings import settings
import json

class AnthropicProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-haiku-20240307"

    async def generate_text(self, prompt: str, system_prompt: str = None, model: str = None) -> AIResponse:
        response = await self.client.messages.create(
            model=model or self.default_model,
            max_tokens=1024,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )

        return AIResponse(
            content=response.content[0].text,
            provider="anthropic",
            model=model or self.default_model
        )

    async def extract_structured_data(self, prompt: str, schema: dict, system_prompt: str = None, model: str = None) -> dict:
        full_prompt = f"{prompt}\n\nReturn ONLY a valid JSON object following this schema: {json.dumps(schema)}"
        response = await self.generate_text(full_prompt, system_prompt, model)
        # Anthropic doesn't have a native JSON mode like OpenAI in this SDK version easily,
        # so we do a simple parse.
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback or retry logic could go here
            return {}
