from abc import ABC, abstractmethod
from shared.schemas import AIResponse

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str = None, model: str = None) -> AIResponse:
        pass

    @abstractmethod
    async def extract_structured_data(self, prompt: str, schema: dict, system_prompt: str = None, model: str = None) -> dict:
        pass
