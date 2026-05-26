from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "FLUXON"
    VERSION: str = "0.8.0"
    DEBUG: bool = False
    WEBHOOK_SECRET_TOKEN: str

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # HubSpot CRM
    HUBSPOT_API_KEY: Optional[str] = None

    # Evolution API
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE: str = "fluxon_main"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
