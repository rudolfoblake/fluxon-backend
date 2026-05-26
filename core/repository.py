from typing import Optional
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from core.models import ConversationSession
from loguru import logger

class SessionRepository:
    @staticmethod
    async def get_session(phone: str) -> ConversationSession:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ConversationSession).where(ConversationSession.phone == phone))
            session = result.scalars().first()
            if not session:
                from modules.orchestration.service import OrchestratorService
                session = ConversationSession(
                    phone=phone, 
                    state="START", 
                    collected_data={}, 
                    history=[],
                    operational_context={"signals": [], "pains": [], "insights": [], "current_stack": []},
                    pending_objectives=OrchestratorService.OBJECTIVES
                )
                db.add(session)
                await db.commit()
                await db.refresh(session)
            return session

    @staticmethod
    async def save_session(session: ConversationSession):
        async with AsyncSessionLocal() as db:
            await db.merge(session)
            await db.commit()
