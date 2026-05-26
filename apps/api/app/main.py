from fastapi import FastAPI, Depends, Request
from config.settings import settings
from core.security import validate_webhook_token
from modules.whatsapp.router import router as whatsapp_router
from modules.whatsapp.schemas import EvolutionWebhookPayload
from modules.conversations.service import ConversationService
from loguru import logger
import time

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Include routers
app.include_router(whatsapp_router)

conversation_service = ConversationService()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    payload: EvolutionWebhookPayload,
    x_webhook_token: str = Depends(validate_webhook_token)
):
    logger.info(f"Received verified webhook event: {payload.event}")
    result = await conversation_service.process_webhook(payload)
    return result

@app.on_event("startup")
async def startup_event():
    from core.models import init_db
    from modules.whatsapp.client import EvolutionClient
    from core.retry_service import RetryService
    from modules.crm.hubspot_service import HubSpotService
    import asyncio
    
    await init_db()
    logger.info("Database initialized")
    
    # Evolution API Bootstrap
    try:
        whatsapp = EvolutionClient()
        await whatsapp.ensure_instance()
        logger.info("Evolution API Bootstrap completed")
    except Exception as e:
        logger.error(f"Evolution API Bootstrap failed: {e}")

    # Background Retry Task
    async def retry_worker():
        retry_service = RetryService()
        crm = HubSpotService()
        while True:
            try:
                tasks = await retry_service.get_pending_tasks()
                for task in tasks:
                    logger.info(f"Retrying task {task.id} ({task.task_type})")
                    try:
                        if task.task_type == "hubspot_sync":
                            await crm.create_or_update_contact(task.payload["phone"], task.payload["props"])
                        await retry_service.mark_completed(task.id)
                    except Exception as te:
                        await retry_service.mark_failed(task.id, str(te))
            except Exception as e:
                logger.error(f"Retry worker error: {e}")
            await asyncio.sleep(300) # 5 minutes

    asyncio.create_task(retry_worker())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
