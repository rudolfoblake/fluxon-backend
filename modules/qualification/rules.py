from typing import Dict, List

QUALIFICATION_RULES: Dict[str, int] = {
    # English keywords
    "automation": 15,
    "operations": 10,
    "pricing": 5,
    "implementation": 20,
    "support": 5,
    "workflow": 15,
    "process": 10,
    "team": 10,
    "budget": 25,
    "urgent": 30,
    "asap": 25,
    "bottleneck": 20,
    "scale": 15,
    "integration": 15,
    "hubspot": 10,
    "crm": 10,
    
    # Portuguese keywords (Localized)
    "automação": 15,
    "operações": 10,
    "preço": 5,
    "implantação": 20,
    "suporte": 5,
    "fluxo": 15,
    "processo": 10,
    "equipe": 10,
    "orçamento": 25,
    "urgente": 30,
    "agora": 25,
    "gargalo": 20,
    "escala": 15,
    "integração": 15
}

NEGATION_KEYWORDS: List[str] = [
    "not", "don't", "no", "never", "can't",
    "não", "nunca", "nem", "jamais", "sem"
]
