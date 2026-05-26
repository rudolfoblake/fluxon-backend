from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from core.models import RetryTask
from datetime import datetime, timedelta
from loguru import logger
import uuid
import json

class RetryService:
    @staticmethod
    async def add_task(task_type: str, payload: dict, max_attempts: int = 3):
        async with AsyncSessionLocal() as db:
            task = RetryTask(
                id=str(uuid.uuid4()),
                task_type=task_type,
                payload=payload,
                max_attempts=max_attempts
            )
            db.add(task)
            await db.commit()
            return task.id

    @staticmethod
    async def get_pending_tasks():
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            result = await db.execute(
                select(RetryTask).where(
                    RetryTask.status == "pending",
                    RetryTask.next_retry <= now,
                    RetryTask.attempts < RetryTask.max_attempts
                )
            )
            return result.scalars().all()

    @staticmethod
    async def mark_completed(task_id: str):
        async with AsyncSessionLocal() as db:
            task = await db.get(RetryTask, task_id)
            if task:
                task.status = "completed"
                await db.commit()

    @staticmethod
    async def mark_failed(task_id: str, error: str):
        async with AsyncSessionLocal() as db:
            task = await db.get(RetryTask, task_id)
            if task:
                task.attempts += 1
                task.last_error = error
                if task.attempts >= task.max_attempts:
                    task.status = "failed"
                else:
                    # Exponential backoff: 5, 15, 45 minutes
                    wait_minutes = 5 * (3 ** (task.attempts - 1))
                    task.next_retry = datetime.utcnow() + timedelta(minutes=wait_minutes)
                await db.commit()
