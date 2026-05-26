import httpx
import asyncio
import json

async def test_webhook():
    url = "http://localhost:8000/whatsapp/webhook"
    headers = {
        "x-webhook-token": "fluxon_webhook_secret"
    }
    payload = {
        "event": "messages.upsert",
        "instance": "fluxon_main",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "ABC12345"
            },
            "pushName": "John Doe",
            "message": {
                "conversation": "Hello, I am interested in automation workflows for my scaling team. What is the pricing and implementation time?"
            },
            "messageType": "conversation"
        },
        "date_time": "2024-05-26T10:00:00Z",
        "sender": "5511999999999@s.whatsapp.net",
        "server_url": "http://evolution-api:8080",
        "apikey": "fluxon_secret_token"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
