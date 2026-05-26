from typing import Dict, Any, Optional
from loguru import logger
from config.settings import settings
from modules.ai.providers.openai_provider import OpenAIProvider
from modules.ai.providers.anthropic_provider import AnthropicProvider
from modules.ai.providers.base import BaseAIProvider

class AIRouter:
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        if settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider()
        if settings.ANTHROPIC_API_KEY:
            self.providers["anthropic"] = AnthropicProvider()
        # Add others as needed

    async def get_provider(self, task_type: str = "default") -> BaseAIProvider:
        # Strategy mapping
        strategy_map = {
            "cheap": "openai", # GPT-4o-mini
            "balanced": "openai", # GPT-4o
            "premium": "anthropic", # Claude-3.5-Sonnet
            "operational_analysis": "openai"
        }
        
        provider_name = strategy_map.get(task_type, "openai")
        
        if provider_name in self.providers:
            return self.providers[provider_name]
        
        if not self.providers:
            raise Exception("No AI providers configured")
        
        return list(self.providers.values())[0]

    async def generate_text(self, prompt: str, task_type: str = "default", **kwargs) -> Any:
        provider = await self.get_provider(task_type)
        
        # Model mapping per provider and task
        model_map = {
            "openai": {
                "cheap": "gpt-4o-mini",
                "balanced": "gpt-4o",
                "premium": "gpt-4o",
                "operational_analysis": "gpt-4o-mini"
            },
            "anthropic": {
                "premium": "claude-3-5-sonnet-20240620",
                "balanced": "claude-3-haiku-20240307"
            }
        }
        
        provider_key = "openai" if isinstance(provider, OpenAIProvider) else "anthropic"
        model = kwargs.get("model") or model_map.get(provider_key, {}).get(task_type)
        
        try:
            return await provider.generate_text(prompt, model=model, **kwargs)
        except Exception as e:
            logger.error(f"AI Provider error: {e}. Attempting fallback...")
            # Fallback simple logic
            fallback_provider = self.providers.get("anthropic" if provider_key == "openai" else "openai")
            if fallback_provider:
                return await fallback_provider.generate_text(prompt, **kwargs)
            raise e
