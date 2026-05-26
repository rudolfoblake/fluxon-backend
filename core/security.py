from fastapi import Header, HTTPException, status
from config.settings import settings

async def validate_webhook_token(x_webhook_token: str = Header(...)):
    if x_webhook_token != settings.WEBHOOK_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token"
        )
    return x_webhook_token
