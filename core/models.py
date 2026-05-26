from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fluxon.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

from sqlalchemy import Column, String, JSON, DateTime, Integer, Boolean

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    phone = Column(String, primary_key=True, index=True)
    state = Column(String, default="START")
    collected_data = Column(JSON, default=dict)
    history = Column(JSON, default=list)
    
    # Novos campos para Inteligência Operacional Avançada
    operational_context = Column(JSON, default=dict) # Sinais, dores, oportunidades, perfil
    pending_objectives = Column(JSON, default=list)  # Objetivos dinâmicos
    lead_score = Column(JSON, default=dict)          # Urgência, valor estimado
    automation_insights = Column(JSON, default=list) # Oportunidades detectadas
    escalation_status = Column(JSON, default=dict)   # {required: bool, reason: str}
    
    last_analysis = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RetryTask(Base):
    __tablename__ = "retry_tasks"

    id = Column(String, primary_key=True)
    task_type = Column(String) # hubspot, ai_process
    payload = Column(JSON)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    status = Column(String, default="pending") # pending, completed, failed
    last_error = Column(String, nullable=True)
    next_retry = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
