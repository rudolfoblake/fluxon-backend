from loguru import logger
from modules.whatsapp.schemas import EvolutionWebhookPayload
from modules.whatsapp.client import EvolutionClient
from modules.whatsapp.normalizer import WhatsAppNormalizer
from modules.orchestration.service import OrchestratorService
from modules.crm.hubspot_service import HubSpotService
from core.repository import SessionRepository
from core.retry_service import RetryService
import asyncio
import uuid

class ConversationService:
    def __init__(self):
        self.orchestrator = OrchestratorService()
        self.crm = HubSpotService()
        self.whatsapp_client = EvolutionClient()
        self.repo = SessionRepository()
        self.normalizer = WhatsAppNormalizer()
        self.retry = RetryService()

    async def process_webhook(self, payload: EvolutionWebhookPayload):
        correlation_id = str(uuid.uuid4())
        
        # 0. Normalização do Payload
        norm_msg = self.normalizer.normalize_evolution_webhook(payload.dict())
        if not norm_msg:
            return {"status": "ignored", "reason": "non_message_event_or_outbound"}

        phone = norm_msg.phone
        message_text = norm_msg.text
        
        logger.info(f"[{correlation_id}] FLUXON Intelligence: Analisando {norm_msg.type} de {phone}")

        # 1. Recuperar Sessão e Memória Operacional
        session = await self.repo.get_session(phone)
        session.history.append({
            "role": "user", 
            "content": message_text, 
            "timestamp": norm_msg.timestamp,
            "type": norm_msg.type,
            "correlation_id": correlation_id,
            "media_metadata": norm_msg.media_metadata
        })

        # 2. Orquestração: Análise de Inteligência Operacional Profunda
        try:
            analysis = await self.orchestrator.analyze_input(message_text, session.operational_context)
            
            # Merge de Inteligência
            session.operational_context["signals"] = list(set(session.operational_context.get("signals", []) + analysis.get("signals", [])))
            session.operational_context["pains"] = list(set(session.operational_context.get("pains", []) + analysis.get("pains", [])))
            session.operational_context["lead_profile"] = analysis.get("lead_profile", session.operational_context.get("lead_profile"))
            session.automation_insights = list(set(session.automation_insights + analysis.get("automation_opportunities", [])))
            session.lead_score = {"urgency": analysis.get("urgency_score", 5)}
            
            # Update dados estruturados
            session.collected_data.update(analysis.get("structured_data", {}))
            
            logger.info(f"[{correlation_id}] Perfil Detectado: {session.operational_context['lead_profile']} | Urgência: {session.lead_score['urgency']}")
        except Exception as e:
            logger.error(f"[{correlation_id}] AI Analysis Failed: {e}")
            # Agendar retry para análise profunda depois se necessário, mas seguir com fluxo básico
            await self.retry.add_task("ai_analysis", {"phone": phone, "text": message_text})
            analysis = {"signals": [], "pains": [], "lead_profile": "unknown", "structured_data": {}}

        # 3. Detecção de Escalação (Human Handoff)
        escalation = await self.orchestrator.detect_escalation(session.operational_context)
        session.escalation_status = escalation

        if escalation.get("required"):
            logger.warning(f"[{correlation_id}] ESCALAÇÃO DETECTADA: {escalation.get('reason')}")
            response_text = "Entendo a complexidade do seu cenário. Vou encaminhar nossa conversa agora mesmo para um de nossos especialistas em automação estratégica para uma análise personalizada."
        else:
            # 4. Decisão Dinâmica do Próximo Objetivo
            pending = [obj for obj in session.pending_objectives if obj not in session.collected_data]
            next_objective = await self.orchestrator.decide_next_objective(session.operational_context, pending)

            if next_objective == "COMPLETE":
                session.state = "QUALIFIED"
                response_text = await self.orchestrator.generate_response("finalize_consultation", session.operational_context)
            else:
                session.state = f"WORKING_{next_objective.upper()}"
                response_text = await self.orchestrator.generate_response(next_objective, session.operational_context)

        # 5. Sincronização Estratégica com CRM (Executiva)
        try:
            summary = await self.orchestrator.generate_executive_summary(session.operational_context)
            hubspot_props = {
                "firstname": norm_msg.push_name or "Lead Qualificado",
                "phone": phone,
                "annualrevenue": str(session.collected_data.get("revenue", "0")),
                "numberofemployees": str(session.collected_data.get("team_size", "0")),
                "lifecyclestage": "lead",
                "notes_last_analysis": summary
            }
            await self.crm.create_or_update_contact(phone, hubspot_props)
        except Exception as e:
            logger.error(f"[{correlation_id}] CRM Sync Error: {e}. Scheduling retry.")
            await self.retry.add_task("hubspot_sync", {"phone": phone, "props": hubspot_props})

        # 6. Execução da Resposta
        try:
            await self.whatsapp_client.send_message(phone, response_text)
            session.history.append({"role": "assistant", "content": response_text, "correlation_id": correlation_id})
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
