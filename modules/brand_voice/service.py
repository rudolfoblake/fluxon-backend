from typing import Dict, Any

class BrandVoiceService:
    PROFILES = {
        "consultive": {
            "guideline": "Foque em entender o processo atual. Use linguagem que demonstre competência em eficiência operacional.",
            "writing_style": "Conciso, observador e estratégico."
        },
        "executive": {
            "guideline": "Foque em ROI, escala e resultados de alto nível. Seja direto e respeite o tempo do interlocutor.",
            "writing_style": "Formal, direto e focado em valor."
        },
        "operational": {
            "guideline": "Foque em gargalos técnicos, integração e redução de erros manuais.",
            "writing_style": "Pragmático, técnico e focado em workflow."
        }
    }

    @classmethod
    def get_profile(cls, name: str = "consultive") -> Dict[str, str]:
        return cls.PROFILES.get(name, cls.PROFILES["consultive"])

    @classmethod
    def apply_voice(cls, base_prompt: str, profile_name: str = "consultive") -> str:
        profile = cls.get_profile(profile_name)
        return f"{base_prompt}\n\nEstilo de Escrita: {profile['writing_style']}\nDiretriz de Tom: {profile['guideline']}"
