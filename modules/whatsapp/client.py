import httpx
from config.settings import settings
from loguru import logger
from typing import Dict, Any, Optional

class EvolutionClient:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def ensure_instance(self):
        """Garante que a instância exista e esteja configurada corretamente."""
        try:
            status = await self.get_connection_status()
            if status.get("status") == "disconnected":
                logger.info(f"Instância {self.instance} desconectada. Aguardando QR Code.")
        except Exception as e:
            logger.warning(f"Instância {self.instance} não encontrada. Criando...")
            await self.create_instance()

    async def create_instance(self):
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": self.instance,
            "token": self.api_key,
            "qrcode": True
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Instância {self.instance} criada com sucesso.")
            return response.json()

    async def get_connection_status(self) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/connectionState/{self.instance}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return {"status": "disconnected"}

    async def get_qr_code(self) -> Optional[str]:
        # Connect instance if not connected
        url = f"{self.base_url}/instance/connect/{self.instance}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("base64") # Base64 image
            return None

    async def logout(self):
        url = f"{self.base_url}/instance/logout/{self.instance}"
        async with httpx.AsyncClient() as client:
            await client.delete(url, headers=self.headers)

    async def send_message(self, number: str, text: str):
        url = f"{self.base_url}/message/sendText/{self.instance}"
        payload = {
            "number": number,
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False},
            "text_message": {"text": text}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
