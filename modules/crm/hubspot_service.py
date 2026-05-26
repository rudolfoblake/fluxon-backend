import httpx
from config.settings import settings
from loguru import logger
from typing import Optional, Dict, Any

class HubSpotService:
    def __init__(self):
        self.api_key = settings.HUBSPOT_API_KEY
        self.base_url = "https://api.hubapi.com/crm/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_contact_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("HubSpot API Key not configured")
            return None

        search_url = f"{self.base_url}/objects/contacts/search"
        payload = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "phone",
                    "operator": "EQ",
                    "value": phone
                }]
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(search_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                results = response.json().get("results", [])
                return results[0] if results else None
            return None

    async def create_or_update_contact(self, phone: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        existing = await self.get_contact_by_phone(phone)
        
        async with httpx.AsyncClient() as client:
            if existing:
                contact_id = existing["id"]
                url = f"{self.base_url}/objects/contacts/{contact_id}"
                response = await client.patch(url, headers=self.headers, json={"properties": properties})
            else:
                url = f"{self.base_url}/objects/contacts"
                properties["phone"] = phone
                response = await client.post(url, headers=self.headers, json={"properties": properties})
            
            response.raise_for_status()
            return response.json()

    async def add_note_to_contact(self, contact_id: str, content: str):
        url = f"{self.base_url}/objects/notes"
        payload = {
            "properties": {
                "hs_note_body": content,
                "hs_timestamp": httpx.utils.now().isoformat()
            },
            "associations": [{
                "to": {"id": contact_id},
                "types": [{
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": 202 # Note to Contact
                }]
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
