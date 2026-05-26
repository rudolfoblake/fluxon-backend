from typing import Dict, Any

class ConversationFlow:
    # State definitions
    START = "START"
    ASKING_REVENUE = "ASKING_REVENUE"
    ASKING_TEAM_SIZE = "ASKING_TEAM_SIZE"
    QUALIFIED = "QUALIFIED"

    # State transitions and questions
    FLOW = {
        START: {
            "question": "Olá! Sou o assistente da Fluxon. Para começarmos, qual o seu faturamento mensal aproximado?",
            "next_state": ASKING_REVENUE
        },
        ASKING_REVENUE: {
            "question": "Entendido. E quantas pessoas trabalham na sua equipe hoje?",
            "next_state": ASKING_TEAM_SIZE
        },
        ASKING_TEAM_SIZE: {
            "question": "Perfeito! Já coletei as informações iniciais. Um de nossos consultores entrará em contato em breve para detalhar como podemos automatizar sua operação.",
            "next_state": QUALIFIED
        },
        QUALIFIED: {
            "question": "Seu perfil já foi encaminhado para nosso time de especialistas. Tem mais alguma dúvida sobre nossas automações?",
            "next_state": QUALIFIED
        }
    }

    @classmethod
    def get_next_step(cls, current_state: str) -> Dict[str, str]:
        return cls.FLOW.get(current_state, cls.FLOW[cls.START])
