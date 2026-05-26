from typing import Dict, Any

class BrandVoiceService:
    PROFILES = {
        "consultive": {
            "guideline": "Foque em identificar 'dinheiro parado' em processos manuais. Use a filosofia da Fluxon sobre pastas de pendências que crescem.",
            "writing_style": "Estrategista, observador, fala de ROI e eficiência."
        },
        "technical": {
            "guideline": "Foque em integrações (API, ERP, CRM) e como a IA da Fluxon se conecta à stack existente sem 'reescrever o mundo'.",
            "writing_style": "Pragmático, focado em conectividade e precisão de dados."
        },
        "executive": {
            "guideline": "Foque em escala sem caos, redução de custos ocultos e visibilidade em tempo real para tomada de decisão.",
            "writing_style": "Direto, focado em resultados de alto nível e visão estratégica."
        }
    }

    @classmethod
    def get_profile(cls, name: str = "consultive") -> Dict[str, str]:
        return cls.PROFILES.get(name, cls.PROFILES["consultive"])

    @classmethod
    def apply_voice(cls, base_prompt: str, profile_name: str = "consultive") -> str:
        profile = cls.get_profile(profile_name)
        return f"{base_prompt}\n\nEstilo de Escrita: {profile['writing_style']}\nDiretriz de Tom: {profile['guideline']}"
