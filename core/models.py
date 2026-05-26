from sqlalchemy import Column, String, JSON, DateTime, Integer
from datetime import datetime
from core.database import Base

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    phone = Column(String, primary_key=True, index=True)
    state = Column(String, default="START")
    collected_data = Column(JSON, default=dict)
    history = Column(JSON, default=list)
    
    # Inteligência Operacional Avançada
    operational_context = Column(JSON, default=dict) # Sinais, dores, stack, perfil
    pending_objectives = Column(JSON, default=list)  # Objetivos dinâmicos
    lead_score = Column(JSON, default=dict)          # Urgência, score
    automation_insights = Column(JSON, default=list) # Oportunidades detectadas
    escalation_status = Column(JSON, default=dict)   # {required: bool, reason: str}
    
    last_analysis = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RetryTask(Base):
    __tablename__ = "retry_tasks"

    id = Column(String, primary_key=True)
    task_type = Column(String) # hubspot_sync, ai_analysis
    payload = Column(JSON)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    status = Column(String, default="pending")
    last_error = Column(String, nullable=True)
    next_retry = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
