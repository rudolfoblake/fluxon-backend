import re
from typing import List, Dict, Any, Tuple
from loguru import logger
from modules.protection.schemas import ProtectionResult

class ProtectionService:
    # Heurísticas de Injeção de Prompt
    INJECTION_PATTERNS = [
        (r"(?i)ignore\s+(all\s+)?previous\s+instructions", "Instruction Override"),
        (r"(?i)you\s+are\s+now", "Role Manipulation"),
        (r"(?i)act\s+as", "Role Manipulation"),
        (r"(?i)system\s+prompt", "Prompt Disclosure Attempt"),
        (r"(?i)reveal\s+instructions", "Prompt Disclosure Attempt"),
        (r"(?i)developer\s+message", "Role Manipulation"),
        (r"(?i)simulate", "Instruction Override"),
        (r"(?i)override", "Instruction Override"),
        (r"(?i)^role:", "Direct Role Injection"),
        (r"(?i)jailbreak", "Jailbreak Attempt"),
    ]

    MAX_MESSAGE_LENGTH = 2000 # Limite prático para WhatsApp Business
    
    RESPONSES = {
        "oversized": "Opa, essa mensagem veio gigante 😅 Consegue resumir um pouco pra eu te ajudar melhor?",
        "suspicious": "Recebi bastante informação aqui 👀 Se puder mandar de forma mais objetiva, consigo analisar com muito mais precisão.",
        "abusive": "Vamos por partes pra eu conseguir analisar direito e te ajudar com qualidade."
    }

    @classmethod
    async def validate_input(cls, text: str) -> ProtectionResult:
        """Executa validação multicamada antes do processamento de IA."""
        
        # 1. Validação de Tamanho (Oversized)
        if len(text) > cls.MAX_MESSAGE_LENGTH:
            logger.warning(f"Protection: Oversized message detected ({len(text)} chars)")
            return ProtectionResult(
                is_safe=False,
                reason="Oversized Message",
                action="block",
                suggested_response=cls.RESPONSES["oversized"],
                threat_level="low"
            )

        # 2. Detecção de Injeção de Prompt
        detected_patterns = []
        for pattern, label in cls.INJECTION_PATTERNS:
            if re.search(pattern, text):
                detected_patterns.append(label)

        if detected_patterns:
            logger.warning(f"Protection: Suspicious patterns detected: {detected_patterns}")
            # Se for apenas um padrão e a mensagem for longa, tentamos sanitizar em vez de bloquear
            if len(detected_patterns) == 1 and len(text) > 100:
                sanitized = cls._sanitize_text(text)
                return ProtectionResult(
                    is_safe=True, # Consideramos seguro após sanitização
                    reason="Sanitized Prompt Injection",
                    action="sanitize",
                    sanitized_text=sanitized,
                    threat_level="medium",
                    detected_patterns=detected_patterns
                )
            
            return ProtectionResult(
                is_safe=False,
                reason="Prompt Injection Attempt",
                action="block",
                suggested_response=cls.RESPONSES["suspicious"],
                threat_level="high",
                detected_patterns=detected_patterns
            )

        return ProtectionResult(is_safe=True, action="allow")

    @classmethod
    def _sanitize_text(cls, text: str) -> str:
        """Remove diretrizes suspeitas mantendo o sentido semântico."""
        sanitized = text
        for pattern, _ in cls.INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[REMOVED]", sanitized)
        return sanitized
