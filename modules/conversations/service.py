from modules.protection.service import ProtectionService
import asyncio
import uuid
from loguru import logger
from modules.whatsapp.schemas import EvolutionWebhookPayload
from modules.whatsapp.client import EvolutionClient
from modules.whatsapp.normalizer import WhatsAppNormalizer
from modules.orchestration.service import OrchestratorService
from modules.crm.hubspot_service import HubSpotService
from core.repository import SessionRepository
from core.retry_service import RetryService

class ConversationService:
    def __init__(self):
        self.orchestrator = OrchestratorService()
        self.crm = HubSpotService()
        self.whatsapp_client = EvolutionClient()
        self.repo = SessionRepository()
        self.normalizer = WhatsAppNormalizer()
        self.retry = RetryService()
        self.protection = ProtectionService()

    async def process_webhook(self, payload: EvolutionWebhookPayload):
        correlation_id = str(uuid.uuid4())
        
        # 0. Normalização do Payload
        norm_msg = self.normalizer.normalize_evolution_webhook(payload.dict())
        if not norm_msg:
            return {"status": "ignored", "reason": "non_message_event_or_outbound"}

        phone = norm_msg.phone
        message_text = norm_msg.text

        # 0.1 Camada de Proteção e Sanitização (Pre-AI)
        protection = await self.protection.validate_input(message_text)
        if not protection.is_safe:
            logger.warning(f"[{correlation_id}] Proteção Ativada: {protection.reason}")
            # Se a proteção sugerir uma resposta, enviamos e interrompemos o processamento de IA
            if protection.suggested_response:
                await self.whatsapp_client.send_message(phone, protection.suggested_response)
                return {"status": "blocked", "reason": protection.reason}

        # Usar texto sanitizado se necessário
        processed_text = protection.sanitized_text or message_text
        
        logger.info(f"[{correlation_id}] FLUXON Intelligence: Analisando {norm_msg.type} de {phone}")

        # 1. Recuperar Sessão e Memória Operacional
        session = await self.repo.get_session(phone)
        
        # Criar entrada de histórico
        history_entry = {
            "role": "user", 
            "content": processed_text, 
            "timestamp": norm_msg.timestamp,
            "type": norm_msg.type,
            "correlation_id": correlation_id,
            "media_metadata": norm_msg.media_metadata,
            "threat_level": protection.threat_level
        }
        
        # Garantir que history seja uma lista e adicionar entrada
        current_history = list(session.history) if session.history else []
        current_history.append(history_entry)
        session.history = current_history

        # 2. Orquestração: Análise de Inteligência Operacional Profunda
        try:
            analysis = await self.orchestrator.analyze_input(processed_text, session.operational_context)
            
            # Merge de Inteligência Específica Fluxon
            operational_context = dict(session.operational_context) if session.operational_context else {}
            
            operational_context["signals"] = list(set(operational_context.get("signals", []) + analysis.get("signals", [])))
            operational_context["pains"] = list(set(operational_context.get("pains", []) + analysis.get("pains", [])))
            operational_context["current_stack"] = list(set(operational_context.get("current_stack", []) + analysis.get("current_stack", [])))
            operational_context["lead_profile"] = analysis.get("lead_profile", operational_context.get("lead_profile"))
            
            session.operational_context = operational_context
            
            # Automações detectadas
            automation_insights = list(session.automation_insights) if session.automation_insights else []
            if analysis.get("automation_opportunity"):
                automation_insights.append(analysis.get("automation_opportunity"))
            session.automation_insights = automation_insights
            
            # Update dados estruturados (Revenue, etc)
            collected_data = dict(session.collected_data) if session.collected_data else {}
            collected_data.update(analysis.get("structured_data", {}))
            session.collected_data = collected_data
            
            logger.info(f"[{correlation_id}] Fluxon Intelligence: Perfil {session.operational_context['lead_profile']} | Sinais {analysis.get('signals')}")
        except Exception as e:
            logger.error(f"[{correlation_id}] AI Analysis Failed: {e}")
            # Agendar retry para análise profunda depois se necessário, mas seguir com fluxo básico
            await self.retry.add_task("ai_analysis", {"phone": phone, "text": message_text})
            analysis = {"signals": [], "pains": [], "lead_profile": "unknown", "structured_data": {}}

        # 3. Detecção de Escalação (Human Handoff)
        escalation = await self.orchestrator.detect_escalation(session.operational_context)
        
        # Check for forced escalation from fatigue/engagement
        if analysis.get("force_escalation"):
            escalation["required"] = True
            escalation["reason"] = analysis.get("escalation_reason")

        session.escalation_status = escalation

        if escalation.get("required"):
            logger.warning(f"[{correlation_id}] ESCALAÇÃO DETECTADA: {escalation.get('reason')}")
            response_text = "Entendo perfeitamente. Para não tomarmos muito seu tempo, vou encaminhar agora nossa conversa para um de nossos especialistas. Ele analisará esses pontos e te dará um retorno estratégico."
        else:
            # 4. Decisão Dinâmica do Próximo Objetivo
            pending = [obj for obj in session.pending_objectives if obj not in session.collected_data]
            
            # Conversational Escape: If fatigue is high or engagement low, prioritize finishing or handoff
            if analysis.get("engagement", {}).get("fatigue") or len(session.history) > 10:
                 next_objective = "COMPLETE"
            else:
                 next_objective = await self.orchestrator.decide_next_objective(session.operational_context, pending)

            if next_objective == "COMPLETE":
                session.state = "QUALIFIED"
                response_text = await self.orchestrator.generate_response("finalize_consultation", session.operational_context)
            else:
                session.state = f"WORKING_{next_objective.upper()}"
                response_text = await self.orchestrator.generate_response(next_objective, session.operational_context)

        # 5. Sincronização Estratégica com CRM (Executiva & Estruturada)
        try:
            summary = await self.orchestrator.generate_executive_summary(session.operational_context)
            
            # Enriquecimento Estruturado HubSpot v9
            hubspot_props = {
                "firstname": norm_msg.push_name or "Lead Qualificado",
                "phone": phone,
                "annualrevenue": str(session.collected_data.get("revenue", "0")),
                "numberofemployees": str(session.collected_data.get("team_size", "0")),
                "estimated_budget": str(session.collected_data.get("budget", "unknown")),
                "lead_temperature": str(session.operational_context.get("lead_profile", {}).get("temperature", "warm")),
                "operational_maturity": str(session.operational_context.get("lead_profile", {}).get("type", "unknown")),
                "discard_reason": str(analysis.get("discard_reason", "")),
                "lifecyclestage": "lead",
                "notes_last_analysis": summary
            }
            await self.crm.create_or_update_contact(phone, hubspot_props)
        except Exception as e:
            logger.error(f"[{correlation_id}] CRM Sync Error: {e}. Scheduling retry.")
            await self.retry.add_task("hubspot_sync", {"phone": phone, "props": hubspot_props})

        # 6. Execução da Resposta com Typing Simulation
        try:
            # Simulate typing delay (approx 1s per 50 chars, max 5s)
            typing_delay = min(len(response_text) / 50, 5)
            await asyncio.sleep(typing_delay)
            
            await self.whatsapp_client.send_message(phone, response_text)
            
            # Atualizar histórico com a resposta do assistente
            assistant_entry = {
                "role": "assistant", 
                "content": response_text, 
                "correlation_id": correlation_id
            }
            current_history = list(session.history)
            current_history.append(assistant_entry)
            session.history = current_history
            
        except Exception as e:
            logger.error(f"[{correlation_id}] WhatsApp Send Error: {e}")
        
        await self.repo.save_session(session)
        
        return {
            "status": "processed",
            "correlation_id": correlation_id,
            "intelligence": {
                "profile": session.operational_context["lead_profile"],
                "urgency": session.lead_score["urgency"],
                "escalation": session.escalation_status.get("required")
            }
        }
