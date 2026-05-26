from typing import Dict, List

QUALIFICATION_RULES: Dict[str, int] = {
    "automation": 10,
    "operations": 8,
    "pricing": 5,
    "implementation": 15,
    "support": 3,
    "workflow": 12,
    "process": 7,
    "team": 5,
    "budget": 20,
    "urgent": 25,
    "asap": 20,
    "bottleneck": 15,
    "scale": 10
}

NEGATION_KEYWORDS: List[str] = [
    "not", "don't", "no", "never", "can't"
]
