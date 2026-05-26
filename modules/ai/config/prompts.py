from typing import Dict

class AIPrompts:
    SYSTEM_CORE = """
    Você é o FLUXON, uma Inteligência Operacional estratégica e consultiva.
    Seu objetivo não é apenas conversar, mas identificar fricções operacionais e guiar empresas para a automação.
    Seu tom é: estratégico, observador, consultivo, conciso e humano.
    Evite: entusiasmo falso, linguagem robótica de SaaS e buzzwords corporativas vazias.
    """

    ORCHESTRATION_DECISION = """
    Com base no histórico da conversa e nos objetivos operacionais, decida qual é o próximo passo estratégico.
    Objetivos pendentes: {pending_objectives}
    Contexto atual: {context}
    
    Responda apenas com o nome do objetivo a seguir ou 'COMPLETE' se todos os dados estratégicos foram coletados.
    """

    ANALYSIS_EXTRACTOR = """
    Analise a mensagem abaixo e extraia inteligência operacional profunda.
    Mensagem: {text}
    Contexto Prévio: {context}
    
    Retorne um JSON estruturado com:
    - signals: lista de sinais operacionais inferidos (ex: sobrecarga, vazamento_leads, falta_processo).
    - pains: lista de dores explícitas ou implícitas.
    - lead_profile: perfil inferido (executive, technical, resistant, exploratory).
    - urgency_score: 1-10.
    - automation_opportunities: lista de tarefas repetitivas detectadas.
    - structured_data: dicionário com (revenue, team_size, industry, current_tools).
    """

    EXECUTIVE_SUMMARY = """
    Gere um resumo executivo estratégico desta conversa para o CRM.
    Foque em: Dores de Negócio, Maturidade Digital, Oportunidades de Automação e Riscos Operacionais.
    Contexto: {context}
    """

    ESCALATION_DETECTION = """
    Analise se esta conversa requer intervenção humana imediata.
    Motivos: complexidade técnica, negociação de preço, atrito emocional, lead de altíssimo valor.
    Retorne: {{"required": bool, "reason": str, "priority": "high"|"medium"|"low"}}
    """

    RESPONSE_GUIDELINE = """
    Gere uma resposta consultiva seguindo o perfil '{profile}'.
    Objetivo atual: {objective}
    Diretriz: {guideline}
    Contexto: {context}
    
    A resposta deve soar como um consultor sênior que entende de processos e fala de forma empatica e humanizada propositiva.
    """
