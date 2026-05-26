from typing import List, Tuple, Dict
from modules.qualification.rules import QUALIFICATION_RULES, NEGATION_KEYWORDS
from shared.schemas import LeadQualification
from loguru import logger

class QualificationEngine:
    def qualify(self, text: str) -> LeadQualification:
        text_lower = text.lower()
        score = 0
        detected_signals = []
        
        # Split text into sentences for better negation context
        sentences = [s.strip() for s in text_lower.replace("?", ".").replace("!", ".").split(".")]
        
        for sentence in sentences:
            words = sentence.split()
            sentence_score = 0
            
            for keyword, points in QUALIFICATION_RULES.items():
                if keyword in sentence:
                    # Check for negations within a small window before the keyword
                    has_negation = False
                    try:
                        idx = words.index(keyword)
                        # Check up to 3 words before
                        start = max(0, idx - 3)
                        for i in range(start, idx):
                            if words[i] in NEGATION_KEYWORDS:
                                has_negation = True
                                break
                    except ValueError:
                        # Keyword might be part of a phrase, check simple presence
                        for neg in NEGATION_KEYWORDS:
                            if f"{neg} {keyword}" in sentence:
                                has_negation = True
                                break
                    
                    if not has_negation:
                        sentence_score += points
                        detected_signals.append(keyword)
                    else:
                        logger.info(f"Negation detected for signal '{keyword}' in sentence: '{sentence}'")
            
            score += sentence_score

        # Determine intent and urgency based on score and signals
        intent = "unknown"
        if score >= 50:
            intent = "hot"
        elif score >= 25:
            intent = "warm"
        elif score > 0:
            intent = "cold"
        else:
            intent = "unqualified"
            
        urgency = "low"
        urgency_keywords = ["urgent", "asap", "immediately", "quick", "hoje", "agora", "urgente"]
        if any(u in text_lower for u in urgency_keywords):
            urgency = "high"
            score += 15
            
        # Add a summary with more intelligence
        summary = self._generate_summary(score, intent, urgency, detected_signals)
            
        return LeadQualification(
            score=score,
            intent=intent,
            urgency=urgency,
            signals=list(set(detected_signals)),
            summary=summary
        )

    def _generate_summary(self, score: int, intent: str, urgency: str, signals: List[str]) -> str:
        if not signals:
            return "Lead demonstrated low engagement or vague interest."
        
        signals_str = ", ".join(list(set(signals)))
        return f"Lead qualified with {intent} intent (Score: {score}). Urgency is {urgency}. Key signals: {signals_str}."
