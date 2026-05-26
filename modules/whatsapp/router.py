from fastapi import APIRouter, Depends, HTTPException, Response
from modules.whatsapp.client import EvolutionClient
from fastapi.responses import HTMLResponse
import base64

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
whatsapp_client = EvolutionClient()

@router.get("/qrcode", response_class=HTMLResponse)
async def get_qrcode():
    qr_base64 = await whatsapp_client.get_qr_code()
    if not qr_base64:
        return "<html><body><h1>Instance already connected or error fetching QR</h1></body></html>"
    
    # Remove header if present in base64 string
    if "base64," in qr_base64:
        qr_base64 = qr_base64.split("base64,")[1]
        
    return f"""
    <html>
        <head><title>Fluxon WhatsApp Login</title></head>
        <body style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif;">
            <h1>Scan to connect Fluxon</h1>
            <img src="data:image/png;base64,{qr_base64}" width="300" height="300" />
            <p>Waiting for connection...</p>
            <script>
                setTimeout(() => location.reload(), 10000);
            </script>
        </body>
    </html>
    """

@router.get("/status")
async def get_status():
    return await whatsapp_client.get_connection_status()

@router.post("/reconnect")
async def reconnect():
    await whatsapp_client.logout()
    return {"message": "Logged out. Refresh QR code page to reconnect."}
