# FLUXON - AI-Powered WhatsApp Automation & Lead Qualification

FLUXON é uma plataforma de automação operacional de nível empresarial focada em transformar conversas de WhatsApp em leads qualificados e estruturados dentro do seu CRM (HubSpot).

---

## 🎯 Visão de Negócio (Business Overview)

O FLUXON resolve o gargalo de atendimento inicial em operações de vendas e suporte. Em vez de um chatbot genérico, o FLUXON atua como um **Agente de Qualificação Ativo**.

### O que o FLUXON faz por você:
1.  **Atendimento Instantâneo**: Responde leads no WhatsApp 24/7 sem intervenção humana inicial.
2.  **Qualificação Inteligente**: Conduz uma conversa natural para extrair dados críticos (Faturamento, Tamanho de Time, Intenção de Compra).
3.  **Enriquecimento com IA**: Utiliza modelos avançados (OpenAI/Claude) para analisar o sentimento e a urgência do lead.
4.  **Sincronização em Tempo Real**: Alimenta o HubSpot automaticamente com dados estruturados e notas detalhadas da conversa.
5.  **Redução de Custo**: Filtra curiosos e entrega apenas leads qualificados para o seu time comercial.

---

## 🛠️ Visão Técnica (Technical Overview)

FLUXON é construído com uma arquitetura de **Monolito Modular**, priorizando performance, resiliência e facilidade de manutenção.

### Tech Stack:
-   **Backend**: Python 3.12 + FastAPI (Async Nativo)
-   **Database**: SQLite + SQLAlchemy 2.0 (Persistência de Sessão)
-   **WhatsApp**: Evolution API (Self-hosted, QR Code Auth)
-   **CRM**: HubSpot API v3
-   **AI Engine**: Multi-provider (OpenAI GPT-4o-mini & Anthropic Claude 3.5 Sonnet)
-   **Infra**: Docker & Docker Compose

### Arquitetura de Fluxo:
1.  **Webhook Ingest**: Recebe eventos da Evolution API.
2.  **Security Layer**: Valida tokens de segurança para evitar spam no CRM.
3.  **State Machine**: Gerencia o estágio da conversa (START -> ASKING_REVENUE -> ASKING_TEAM -> QUALIFIED).
4.  **AI Extraction**: Extrai informações específicas de mensagens usando LLMs.
5.  **CRM Sync**: Atualiza o HubSpot de forma idempotente a cada interação.

---

## 🚀 Como Operar (Setup & Installation)

### Pré-requisitos:
-   Docker e Docker Compose instalados.
-   Chaves de API (OpenAI/Anthropic e HubSpot).

### Instalação Rápida:
1.  **Configurar Variáveis**:
    ```bash
    cp .env.example .env
    # Edite o .env com suas chaves de API
    ```

2.  **Subir o Sistema**:
    ```bash
    docker compose up -d --build
    ```

3.  **Conectar WhatsApp**:
    -   Acesse `http://localhost:8000/whatsapp/qrcode` no seu navegador.
    -   Escaneie o QR Code com o WhatsApp do seu negócio.

4.  **Verificar Status**:
    -   Acesse `http://localhost:8000/whatsapp/status` para confirmar a conexão.

---

## 📊 Guia Operacional para o Cliente

### Como o bot se comporta?
O bot segue um fluxo pré-definido em `modules/conversations/flow.py`. Ele é configurado para ser direto e profissional.

### Onde vejo os leads?
Todos os leads aparecem na aba "Contatos" do seu HubSpot.
-   **Propriedades Preenchidas**: Nome, Telefone, Receita Anual (Faturamento), Número de Funcionários.
-   **Histórico**: Todas as mensagens e análises da IA são anexadas como "Notas" no perfil do contato.

---

## 🛡️ Segurança e Resiliência
-   **Fallback de IA**: Se a OpenAI falhar, o sistema tenta automaticamente o Claude da Anthropic.
-   **Persistência**: As sessões são salvas em banco de dados local. Se o servidor reiniciar, o bot continua a conversa de onde parou.
-   **Validação de Webhook**: Apenas mensagens legítimas da sua instância de WhatsApp são processadas.

---

## 📝 Changelog

### [v0.5.0] - 2026-05-26 (Production Stabilization)
- **Lightweight Retry System**: Implementação de fila de re-tentativa local (SQLite) para falhas de CRM e IA com backoff exponencial.
- **Enhanced Normalization & Media**: Parsing robusto de metadados de mídia (dimensões de imagem, duração de áudio, nomes de arquivos).
- **AI Validation Layer**: Proteção contra alucinações e limpeza de outputs da IA antes da persistência.
- **Background Workers**: Processamento assíncrono em background para tarefas de manutenção e retry.
- **Correlation ID Observability**: Rastreamento completo de requisições do webhook até a resposta final.

### [v0.4.0] - 2026-05-26 (Production-Grade Operational Intelligence)
- **Evolution API Bootstrap**: Gerenciamento automático de ciclo de vida das instâncias (auto-create e health check).
- **WhatsApp Normalization Layer**: Centralização de parsing para múltiplos tipos de mensagens (texto, imagem, botões, etc).
- **Advanced Operational Memory**: Captura de perfil de lead (executive, technical), score de urgência e oportunidades de automação.
- **Escalation Intelligence**: Detecção automática de necessidade de intervenção humana (Handoff).
- **Executive Summaries**: Geração de resumos estratégicos para o HubSpot em vez de notas genéricas.
- **Observability**: Implementação de Correlation IDs para rastreamento de fluxos assíncronos.

### [v0.3.0] - 2026-05-26 (Operational Intelligence Evolution)
- **Dynamic Orchestration**: Removida a dependência de FSM rígida. Agora o bot decide o próximo objetivo com base no contexto operacional.
- **Brand Voice System**: Implementação de perfis de voz (Consultivo, Executivo, Operacional) para garantir uma identidade premium.
- **Prompt Centralization**: Todos os prompts estratégicos centralizados em `modules/ai/config/prompts.py`.
- **Operational Memory**: Evolução do banco de dados para armazenar sinais de negócio, dores e insights contextuais.
- **Strategic AI Routing**: Roteamento baseado em perfis (Cheap para extração, Premium para respostas consultivas).

### [v0.2.0] - 2026-05-26 (MVP Interativo)
-   **FSM (Finite State Machine)**: Implementação de máquina de estados para conduzir conversas.
-   **Persistência SQLite**: Adicionado suporte a banco de dados para salvar histórico e estados.
-   **AI Extraction**: Nova lógica para extrair dados estruturados de mensagens informais.
-   **Interactive Messaging**: O bot agora responde ativamente aos usuários no WhatsApp.
-   **Security**: Ativação da validação de token em todos os webhooks.
-   **AI Fallback**: Roteamento inteligente com redundância entre provedores.

### [v0.1.0] - 2026-05-26 (Foundation)
-   Estrutura base com FastAPI e Docker.
-   Integração inicial com Evolution API (WhatsApp).
-   Serviço básico de integração com HubSpot CRM.
-   Motor de qualificação baseado em regras (Keywords).
-   Router de IA multi-provedor (OpenAI, Anthropic, Gemini).

---

**Desenvolvido por Fluxon Team - 2026**
