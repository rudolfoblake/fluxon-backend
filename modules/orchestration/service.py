from typing import List, Dict, Any, Optional
from modules.ai.services.ai_router import AIRouter
from modules.ai.config.prompts import AIPrompts
from modules.brand_voice.service import BrandVoiceService
from loguru import logger
import json

class OrchestratorService:
    OBJECTIVES = [
        "identify_operational_pain",
        "identify_automation_opportunity",
        "identify_team_size",
        "identify_revenue_impact",
        "identify_urgency"
    ]

    def __init__(self):
        self.ai_router = AIRouter()
        self.brand_voice = BrandVoiceService()

    async def analyze_input(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o input para extrair inteligência operacional profunda com validação."""
        prompt = AIPrompts.ANALYSIS_EXTRACTOR.format(text=text, context=json.dumps(context))
        try:
            response = await self.ai_router.generate_text(prompt, task_type="operational_analysis")
            content = response.content.strip().replace("```json", "").replace("```", "")
            data = json.loads(content)
            
            # Validação Leve de Segurança e Alucinação
            validated_data = self._validate_analysis(data)
            return validated_data
        except Exception as e:
            logger.error(f"Orchestrator Analysis Error: {e}")
            return {"signals": [], "pains": [], "lead_profile": "unknown", "structured_data": {}}

    def _validate_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida se os dados extraídos pela IA fazem sentido operacional."""
        # Garantir campos obrigatórios
        required_fields = ["signals", "pains", "lead_profile", "structured_data"]
        for field in required_fields:
            if field not in data:
                data[field] = [] if "s" in field else {} if "data" in field else "unknown"
        
        # Limpar sinais alucinados (muito longos ou com caracteres estranhos)
        data["signals"] = [s[:50] for s in data["signals"] if len(s) > 2]
        data["pains"] = [p[:100] for p in data["pains"] if len(p) > 2]
        
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
