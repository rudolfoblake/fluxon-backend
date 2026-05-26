from typing import Dict, Any, Optional
from pydantic import BaseModel

class NormalizedMessage(BaseModel):
    message_id: str
    phone: str
    push_name: Optional[str] = None
    text: str
    type: str # text, image, audio, document, button_response
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    media_metadata: Optional[Dict[str, Any]] = None
    timestamp: str
    raw_payload: Dict[str, Any]

class WhatsAppNormalizer:
    @staticmethod
    def normalize_evolution_webhook(payload: Dict[str, Any]) -> Optional[NormalizedMessage]:
        event = payload.get("event")
        if event not in ["messages.upsert", "messages.update"]:
            return None

        data = payload.get("data", {})
        key = data.get("key", {})
        
        if key.get("fromMe"):
            return None

        message = data.get("message", {})
        
        # 1. Extrair Texto e Mídia de forma recursiva (para lidar com quoted messages se necessário)
        text = ""
        msg_type = "text"
        media_url = None
        media_type = None
        media_metadata = {}

        if "conversation" in message:
            text = message["conversation"]
        elif "extendedTextMessage" in message:
            text = message["extendedTextMessage"].get("text", "")
        elif "imageMessage" in message:
            msg_type = "image"
            text = message["imageMessage"].get("caption", "")
            media_type = "image/jpeg"
            media_metadata = {
                "mimetype": message["imageMessage"].get("mimetype"),
                "height": message["imageMessage"].get("height"),
                "width": message["imageMessage"].get("width")
            }
        elif "audioMessage" in message:
            msg_type = "audio"
            media_type = "audio/ogg"
            media_metadata = {
                "mimetype": message["audioMessage"].get("mimetype"),
                "seconds": message["audioMessage"].get("seconds")
            }
        elif "documentMessage" in message:
            msg_type = "document"
            text = message["documentMessage"].get("title", "")
            media_type = message["documentMessage"].get("mimetype")
            media_metadata = {
                "mimetype": message["documentMessage"].get("mimetype"),
                "fileName": message["documentMessage"].get("fileName")
            }
        elif "buttonsResponseMessage" in message:
            msg_type = "button_response"
            text = message["buttonsResponseMessage"].get("selectedButtonId", "")
        elif "listResponseMessage" in message:
            msg_type = "button_response"
            text = message["listResponseMessage"].get("singleSelectReply", {}).get("selectedRowId", "")

        return NormalizedMessage(
            message_id=key.get("id"),
            phone=key.get("remoteJid", "").split("@")[0],
            push_name=data.get("pushName"),
            text=text,
            type=msg_type,
            media_url=media_url,
            media_type=media_type,
            media_metadata=media_metadata,
            timestamp=payload.get("date_time"),
            raw_payload=payload
        )
