from loguru import logger
import json
from typing import List, Dict, Any, Optional
from modules.ai.services.ai_router import AIRouter
from modules.ai.config.prompts import AIPrompts
from modules.brand_voice.service import BrandVoiceService

class OrchestratorService:
    OBJECTIVES = [
        "identify_bottleneck",        # Identificar gargalos e processos manuais
        "identify_operational_pain",   # Identificar dores como retrabalho ou falta de visibilidade
        "identify_tech_stack",         # Identificar ERP/CRM/Ferramentas atuais
        "identify_automation_goal",    # O que desejam automatizar primeiro
        "identify_urgency"             # Urgência e impacto financeiro
    ]

    def __init__(self):
        self.ai_router = AIRouter()
        self.brand_voice = BrandVoiceService()

    async def analyze_input(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o input para extrair inteligência operacional profunda com validação e fadiga."""
        prompt = AIPrompts.ANALYSIS_EXTRACTOR.format(text=text, context=json.dumps(context))
        try:
            response = await self.ai_router.generate_text(prompt, task_type="operational_analysis")
            content = response.content.strip().replace("```json", "").replace("```", "")
            data = json.loads(content)
            
            # Validação e Processamento de Fadiga/Escape
            data = self._process_engagement(data)
            return self._validate_analysis(data)
        except Exception as e:
            logger.error(f"Orchestrator Analysis Error: {e}")
            return {"signals": [], "engagement": {"fatigue": False}, "lead_profile": {"temperature": "warm"}, "structured_data": {}}

    def _process_engagement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta sinais de escape rápido e fadiga."""
        engagement = data.get("engagement", {})
        if engagement.get("fatigue") or engagement.get("vague") or engagement.get("score", 10) < 3:
            # Forçar escalação se houver fadiga ou desengajamento
            data["force_escalation"] = True
            data["escalation_reason"] = "Conversational fatigue or low engagement detected."
        return data

    def _validate_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida se os dados extraídos pela IA fazem sentido operacional para a Fluxon."""
        # Garantir campos obrigatórios Fluxon v9
        required_fields = ["signals", "engagement", "lead_profile", "structured_data"]
        for field in required_fields:
            if field not in data:
                data[field] = [] if isinstance(data.get(field), list) else {}
        
        # Limpar sinais alucinados
        if isinstance(data.get("signals"), list):
            data["signals"] = [s[:50] for s in data["signals"] if len(str(s)) > 2]
        
        return data

    async def detect_escalation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta se o lead precisa de intervenção humana."""
        prompt = AIPrompts.ESCALATION_DETECTION.format(context=json.dumps(context))
        try:
            response = await self.ai_router.generate_text(prompt, task_type="cheap")
            content = response.content.strip().replace("```json", "").replace("```", "")
            return json.loads(content)
        except Exception as e:
            return {"required": False, "reason": "detection_failed"}

    async def generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Gera um resumo estratégico para o CRM."""
        prompt = AIPrompts.EXECUTIVE_SUMMARY.format(context=json.dumps(context))
        response = await self.ai_router.generate_text(prompt, task_type="balanced")
        return response.content

    async def decide_next_objective(self, context: Dict[str, Any], pending_objectives: List[str]) -> str:
        """Decide dinamicamente qual o próximo objetivo com base no contexto."""
        if not pending_objectives:
            return "COMPLETE"
            
        prompt = AIPrompts.ORCHESTRATION_DECISION.format(
            pending_objectives=", ".join(pending_objectives),
            context=json.dumps(context)
        )
        
        response = await self.ai_router.generate_text(prompt, task_type="balanced")
        decision = response.content.strip().upper()
        
        if decision == "COMPLETE":
            return "COMPLETE"
            
        # Validar se a decisão é um objetivo válido
        for obj in self.OBJECTIVES:
            if obj.upper() in decision:
                return obj
                
        return pending_objectives[0]

    async def generate_response(self, objective: str, context: Dict[str, Any], profile: str = "consultive") -> str:
        """Gera uma resposta estratégica baseada no objetivo e na Brand Voice."""
        voice_profile = self.brand_voice.get_profile(profile)
        
        prompt = AIPrompts.RESPONSE_GUIDELINE.format(
            profile=profile,
            objective=objective,
            guideline=voice_profile["guideline"],
            context=json.dumps(context)
        )
        
        system_prompt = AIPrompts.SYSTEM_CORE
        
        # Usando modelo premium para garantir tom consultivo de alta qualidade
        response = await self.ai_router.generate_text(
            prompt, 
            system_prompt=system_prompt, 
            task_type="premium"
        )
        return response.content
