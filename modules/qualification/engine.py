from typing import List, Tuple
from modules.qualification.rules import QUALIFICATION_RULES
from shared.schemas import LeadQualification

class QualificationEngine:
    def qualify(self, text: str) -> LeadQualification:
        text_lower = text.lower()
        score = 0
        detected_signals = []
        
        for keyword, points in QUALIFICATION_RULES.items():
            if keyword in text_lower:
                score += points
                detected_signals.append(keyword)
        
        # Determine intent and urgency based on score and signals
        intent = "unknown"
        if score > 30:
            intent = "high"
        elif score > 10:
            intent = "medium"
        else:
            intent = "low"
            
        urgency = "low"
        if any(u in text_lower for u in ["urgent", "asap", "immediately", "quick"]):
            urgency = "high"
            score += 10
            
        return LeadQualification(
            score=score,
            intent=intent,
            urgency=urgency,
            signals=detected_signals,
            summary=f"Lead qualified with score {score} based on signals: {', '.join(detected_signals)}"
        )
