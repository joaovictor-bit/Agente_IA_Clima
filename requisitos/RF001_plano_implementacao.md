# PLANO DE IMPLEMENTAÇÃO — PL-001
## Chat Interativo via CMD — Agente de Clima

**Referências:** RF-001 (requisito funcional) · DD-001 (design)
**Versão:** 1.0
**Data:** 07/11/2026
**Responsável:** Tech Lead

---

## 1. Objetivo

Implementar o agente de clima via CMD conforme RF-001 e o design DD-001:
chat em Python no terminal, agente Strands com modelo OpenAI, tools de
clima (OpenWeatherMap) e data/hora (`current_time`), memória de sessão
persistente em arquivo local (`FileSessionManager`) e configuração
via `.env`.

## 2. Visão Geral das Fases

```text
Fase 0 ────► Fase 1 ────► Fase 2 ────► Fase 3 ────► Fase 4
Setup        Tools        Agente       Loop CLI     Validação
projeto                   + Memória    + Erros      (aceite)
                │                                      │
                └──────── Quality Gates (G1 a G4) ─────┘
```

Cada fase termina com um **quality gate** supervisionado pelo Tech Lead:
a fase seguinte só inicia após aprovação.

## 3. Agentes / Papéis Necessários

| Papel | Tipo | Responsabilidade |
|-------|------|------------------|
| **Tech Lead** | Supervisão | Aprova design e plano, revisa cada gate, decide sobre desvios, valida critérios de aceite finais |
| **Dev Agent** (implementador) | Execução | Escreve o código (`main.py`), arquivos de configuração e `requirements.txt` seguindo o DD-001 |
| **Review Agent** (revisor) | Supervisão | Code review por fase: aderência ao design, simplicidade (RNF-02), segurança (RNF-04), tratamento de erros |
| **QA Agent** (testador) | Execução/Verificação | Executa os critérios de aceite CA-01 a CA-07 manualmente no terminal e registra evidências |

> Em um time pequeno (ou com agentes de IA), os papéis podem ser
> acumulados, mas **implementação e revisão nunca devem ser feitas pelo
> mesmo agente sem checkpoint de supervisão**.

### 3.1 Matriz RACI

| Atividade | Dev Agent | Review Agent | QA Agent | Tech Lead |
|-----------|:---------:|:------------:|:--------:|:---------:|
| Fase 0 — Setup | R | C | I | A |
| Fase 1 — Tools | R | C | I | A |
| Fase 2 — Agente + Memória | R | C | I | A |
| Fase 3 — Loop + Erros | R | C | I | A |
| Fase 4 — Validação de aceite | C | C | R | A |

R = executa · A = aprova · C = consultado · I = informado

## 4. Detalhamento das Atividades

### Fase 0 — Setup do Projeto

| # | Atividade | Entrega | Esforço |
|---|-----------|---------|:-------:|
| 0.1 | Criar `requirements.txt` com `strands-agents[openai]`, `strands-agents-tools`, `requests`, `python-dotenv` | `requirements.txt` | P |
| 0.2 | Criar `.env.example` com `OPENAI_API_KEY`, `OPENWEATHER_API_KEY`, `OPENAI_MODEL` (comentado) | `.env.example` | P |
| 0.3 | Criar `.gitignore` (`.env`, `sessions/`, `__pycache__/`, `*.pyc`) | `.gitignore` | P |
| 0.4 | Criar `.env` local com as chaves reais (ação do usuário) | `.env` (não commitado) | P |
| 0.5 | Criar ambiente virtual e instalar dependências (`pip install -r requirements.txt`) | venv funcional | P |

**Gate G1:** dependências instalam sem erro; `.env` não está no git;
`python -c "import strands"` funciona.

### Fase 1 — Tools

| # | Atividade | Entrega | Esforço |
|---|-----------|---------|:-------:|
| 1.1 | Implementar `get_weather(city, country_code="")` com `@tool`: chamada ao OpenWeatherMap (`units=metric`, `lang=pt_br`), timeout de 10s | Função tool | M |
| 1.2 | Tratar retornos: 404 → cidade não encontrada; demais erros/timeout → mensagem genérica (DD-001 §4.3) | Dicts de erro padronizados | P |
| 1.3 | Importar e registrar `current_time` do `strands-agents-tools` | Tool disponível | P |

**Gate G2:** Review Agent valida assinatura e contrato de retorno
conforme DD-001 §4.3; teste manual da função fora do agente com uma
cidade válida e uma inválida.

### Fase 2 — Agente e Memória de Sessão

| # | Atividade | Entrega | Esforço |
|---|-----------|---------|:-------:|
| 2.1 | Carregar `.env` (`load_dotenv()`) e validar variáveis obrigatórias; ausente → mensagem clara + `sys.exit(1)` (CA-06) | Validação de startup | P |
| 2.2 | Configurar `OpenAIModel` com `model_id` de `OPENAI_MODEL` (default `gpt-4o-mini`) | Instância do modelo | P |
| 2.3 | Escrever system prompt pt-BR: persona, quando usar cada tool, respostas concisas | System prompt | P |
| 2.4 | Instanciar `Agent` com tools `[get_weather, current_time]` e `FileSessionManager(session_id="chat_clima", storage_dir="./sessions")` | Agente configurado | M |

**Gate G3:** ao executar, o arquivo `./sessions/session_chat_clima.json`
é criado após a primeira interação; reabrir o programa restaura o
contexto (perguntar "do que estávamos falando?" deve funcionar).

### Fase 3 — Loop de Chat e Tratamento de Erros

| # | Atividade | Entrega | Esforço |
|---|-----------|---------|:-------:|
| 3.1 | Implementar loop `input("Você: ")` exibindo `Agente: <resposta>` | Loop funcional | P |
| 3.2 | Comandos `sair`/`exit`/`quit` (case-insensitive) e `Ctrl+C`/`EOF` → despedida + encerramento limpo | Encerramento | P |
| 3.3 | Entrada vazia ignorada; exceções na chamada ao agente → erro amigável sem derrubar o loop (RF-08) | Robustez do loop | P |
| 3.4 | Mensagem de boas-vindas incluindo instrução de como resetar a memória (apagar `sessions/`) | UX de início | P |

**Gate G4:** Review Agent aprova o `main.py` completo: simplicidade
(RNF-02), nenhuma chave no código (CA-07), erros tratados (RF-07/RF-08).

### Fase 4 — Validação de Aceite

QA Agent executa cada critério e registra resultado:

| CA | Teste | Esperado |
|----|-------|----------|
| CA-01 | `python main.py` | Chat inicia aguardando entrada |
| CA-02 | "Qual o clima no Rio de Janeiro?" | Resposta com temp/descrição/umidade reais |
| CA-03 | "Me conte uma curiosidade" | Resposta sem acionar `get_weather` |
| CA-04 | "Clima em Xyzabc123" | Mensagem amigável, sem crash |
| CA-05 | Digitar `sair` | Despedida e exit code 0 |
| CA-06 | Rodar sem `OPENAI_API_KEY` | Aviso claro e exit code 1 |
| CA-07 | Revisar código-fonte | Nenhuma chave hardcoded |
| Extra | "Que horas são?" | Agente usa `current_time` |
| Extra | Reabrir após conversa | Contexto anterior restaurado |

**Gate final (Go/No-Go):** Tech Lead aprova todos os CA + extras.

## 5. Dependências e Sequenciamento

```text
0.1–0.5 ──► 1.1 ──► 1.2 ──► 2.1 ──► 2.2 ──► 2.3 ──► 2.4 ──► 3.1 ──► 3.2–3.4 ──► Fase 4
                 └── 1.3 (paralelo a 1.1/1.2)
```

- **Bloqueio externo:** atividade 0.4 (chaves de API) depende do usuário —
  deve ser providenciada antes da Fase 1 (teste da tool) e Fase 4.
- Todo o código fica em `main.py` (decisão RNF-02); as fases separam
  **entregas lógicas**, não arquivos.

## 6. Pontos de Supervisão (Tech Lead)

| Momento | Verificação |
|---------|-------------|
| Pré-implementação | Design DD-001 aprovado e congelado |
| G1 | Setup reproduzível; segredos fora do git |
| G2 | Contrato da tool igual ao design; erros padronizados |
| G3 | Memória persiste e restaura entre execuções |
| G4 | Código simples, legível, sem chaves, erros tratados |
| Go/No-Go | Todos os CA verificados com evidência |

**Critério de escalação:** qualquer desvio do DD-001 (ex.: trocar
biblioteca HTTP, adicionar tool, mudar persistência) exige aprovação do
Tech Lead **antes** da implementação e atualização do documento.

## 7. Riscos e Mitigações

| Risco | Prob. | Mitigação |
|-------|:-----:|-----------|
| Chaves de API indisponíveis/inválidas | M | Validar no startup (2.1); QA testa com keys reais cedo |
| Mudança de API do Strands entre versões | M | Fixar versões no `requirements.txt` |
| Arquivo de sessão corrompido | B | FileSessionManager recria; documentar reset |
| Custo/limite da OpenAI | B | Default `gpt-4o-mini`; uso local controlado |
| OpenWeatherMap: cidade ambígua | M | Parâmetro `country_code` no design |

## 8. Definition of Done

- [ ] `main.py` + `requirements.txt` + `.env.example` + `.gitignore` no repo
- [ ] Todos os CA-01 a CA-07 verificados e registrados
- [ ] Memória persiste entre execuções (`sessions/` criado)
- [ ] Nenhum segredo no código ou no git
- [ ] Documentos `RF001`/`DD-001`/`PL-001` consistentes entre si
- [ ] Aprovação final do Tech Lead (gate Go/No-Go)

---

*Legenda de esforço: P = pequeno · M = médio*
