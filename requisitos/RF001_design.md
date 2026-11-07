# DOCUMENTO DE DESIGN — DD-001
## Chat Interativo via CMD — Agente de Clima

**Referência:** RF-001 (requisitos/RF001_chat_clima_cmd.md)
**Versão:** 1.0
**Data:** 07/11/2026

---

## 1. Visão Geral da Arquitetura

```text
┌─────────┐   input    ┌──────────┐   prompt   ┌───────────────────┐
│ Usuário │ ◄────────► │ main.py  │ ◄────────► │  Agent (Strands)  │
│  (CMD)  │   resposta │ (loop)   │            │  modelo: OpenAI   │
└─────────┘            └──────────┘            └───────┬───────────┘
                                                     │ chama tools
                          ┌──────────────────────────┼──────────────────┐
                          ▼                          ▼                  ▼
                  ┌───────────────┐        ┌─────────────────┐  ┌──────────────┐
                  │ get_weather() │        │  current_time   │  │ FileSession  │
                  │ (tool custom) │        │ (strands-tools) │  │  Manager     │
                  └───────┬───────┘        └─────────────────┘  └──────┬───────┘
                          ▼                                           ▼
                  OpenWeatherMap API                          ./sessions/*.json
```

## 2. Decisões Técnicas

| Item | Decisão | Justificativa |
|------|---------|---------------|
| Linguagem | Python 3.10+ | Exigência do Strands Agents |
| Framework de agente | `strands-agents` | Requisito do usuário (AWS Strands) |
| Modelo | `OpenAIModel` (Strands provider OpenAI) | Requisito do usuário |
| Memória | `FileSessionManager` | Persiste sessão em arquivo local e restaura ao reabrir |
| Tool de clima | Tool customizada `get_weather` → OpenWeatherMap | Requisito do usuário |
| Tool de hora | `current_time` do pacote `strands-agents-tools` | Requisito do usuário |
| Config | `.env` + `python-dotenv` | Requisito do usuário |
| HTTP | `requests` | Simples e suficiente |

## 3. Estrutura de Arquivos

```text
Projeto/
├── main.py              # código completo do agente (arquivo único)
├── requirements.txt     # dependências
├── .env                 # chaves de API (NÃO commitar)
├── .env.example         # modelo do .env para referência
├── .gitignore           # ignora .env e sessions/
├── sessions/            # arquivos de memória de sessão (FileSessionManager)
│   └── session_chat_clima.json
└── requisitos/
    ├── RF001_chat_clima_cmd.md
    └── RF001_design.md
```

## 4. Componentes

### 4.1 Variáveis de Ambiente (`.env`)

```text
OPENAI_API_KEY=sk-...
OPENWEATHER_API_KEY=...
OPENAI_MODEL=gpt-4o-mini        # opcional; default usado se ausente
```

- Carregadas com `load_dotenv()` na inicialização.
- `OPENAI_MODEL` é opcional; default: `gpt-4o-mini`.
- Se `OPENAI_API_KEY` ou `OPENWEATHER_API_KEY` estiverem ausentes, o
  programa exibe mensagem indicando qual variável falta e encerra
  com código 1 (atende CA-06).

### 4.2 Agente (`main.py`)

- **Modelo:** `OpenAIModel` do Strands, com `model_id` vindo de
  `OPENAI_MODEL` e autenticação via `OPENAI_API_KEY`.
- **System prompt** (pt-BR): define o agente como assistente de clima,
  instrui a usar `get_weather` para clima e `current_time` para
  data/hora, responder sempre em português de forma concisa.
- **Tools registradas:** `[get_weather, current_time]`.
- **Session manager:** `FileSessionManager` com `session_id` fixo
  (ex.: `"chat_clima"`) e `storage_dir="./sessions"`.

### 4.3 Tool de Clima — `get_weather`

Tool customizada (decorator `@tool` do Strands).

**Assinatura:**

```python
@tool
def get_weather(city: str, country_code: str = "") -> dict
```

**Parâmetros:**

- `city` — nome da cidade (obrigatório).
- `country_code` — código ISO do país, ex.: `BR` (opcional, melhora a
  precisão da busca).

**Chamada HTTP:**

```text
GET https://api.openweathermap.org/data/2.5/weather
    ?q={city},{country_code}
    &appid={OPENWEATHER_API_KEY}
    &units=metric
    &lang=pt_br
```

**Retorno (sucesso):**

```python
{
    "cidade": "São Paulo, BR",
    "descricao": "nublado",
    "temperatura_c": 19.4,
    "sensacao_termica_c": 18.8,
    "umidade_pct": 88,
    "vento_ms": 3.1
}
```

**Retorno (erro):**

```python
{"erro": "Cidade 'X' não encontrada. Verifique o nome."}      # HTTP 404
{"erro": "Falha ao consultar o serviço de clima."}            # timeout/5xx/etc.
```

### 4.4 Tool de Data/Hora — `current_time`

- Importada do pacote `strands-agents-tools`
  (`from strands_tools import current_time`).
- Retorna data e hora atuais para o agente; usada quando o usuário
  pergunta "que horas são", "que dia é hoje" etc.

### 4.5 Memória de Sessão — `FileSessionManager`

- O Strands persiste automaticamente o histórico da conversa em
  `./sessions/session_chat_clima.json` após cada interação.
- Como o `session_id` é fixo, ao reabrir o programa a conversa é
  **restaurada** — o agente lembra do que foi dito em execuções
  anteriores.
- Para iniciar uma conversa do zero, basta apagar a pasta `sessions/`
  (comportamento documentado ao usuário na mensagem de boas-vindas).

### 4.6 Loop de Chat

```text
1. Valida variáveis de ambiente (seção 4.1)
2. Cria o Agent com modelo, tools e session manager
3. Exibe mensagem de boas-vindas
4. Loop:
   a. input("Você: ")
   b. "sair"/"exit"/"quit" (case-insensitive) → despedida + break
   c. entrada vazia → ignora
   d. agent(mensagem) → imprime "Agente: <resposta>"
   e. exceção na chamada → imprime erro amigável, continua o loop
5. Ctrl+C (KeyboardInterrupt) → despedida + encerra
```

## 5. Tratamento de Erros

| Cenário | Comportamento |
|---------|---------------|
| Env var ausente | Avisa qual variável falta e encerra (exit 1) |
| Cidade não encontrada (404) | Tool retorna erro amigável; agente repassa ao usuário |
| Falha de rede/timeout/5xx | Tool retorna erro genérico; loop continua |
| Erro na API da OpenAI | Mensagem de erro exibida; loop continua |
| Arquivo de sessão corrompido | `SessionException` capturada no startup → backup de `sessions/` + sessão nova (ver SEC-001 F2) |
| Ctrl+C / EOF | Despedida e encerramento limpo |

## 6. Dependências (`requirements.txt`)

```text
strands-agents[openai]==1.64.0
strands-agents-tools==0.8.12
requests==2.34.2
python-dotenv==1.2.4
```

> O extra `[openai]` instala o cliente `openai`, necessário ao
> `OpenAIModel` do Strands.
> `strands-agents-tools` fixado em 0.8.12: a tool `current_time` foi
> removida na versão 0.9.0 (substituída por ContextInjector upstream).

## 7. Rastreabilidade (RF-001 → Design)

| Requisito | Componente |
|-----------|------------|
| RF-01/RF-02 (loop, sair) | Seção 4.6 |
| RF-03 (contexto) | FileSessionManager (4.5) |
| RF-04 (tool de clima) | `get_weather` (4.3) |
| RF-05/RF-06 (agente decide) | Agent + system prompt (4.2) |
| RF-07/RF-08 (erros) | Seções 4.3 e 5 |
| RNF-04 (.env) | Seção 4.1 |
| RNF-02 (simplicidade) | Arquivo único `main.py` |
| Design: hora atual | `current_time` (4.4) |
| Design: memória em arquivo | `FileSessionManager` (4.5) |

## 8. Observações

- O `FileSessionManager` muda o comportamento descrito no RF-001
  (histórico apenas em memória): agora a conversa **persiste entre
  execuções**, conforme requisito de design item 4.
- O `session_id` fixo significa um único histórico contínuo. Se no
  futuro for desejado múltiplas conversas, basta gerar um
  `session_id` por execução ou por nome de sessão.
- Mantido o princípio de simplicidade: um único arquivo `main.py`,
  ~80-120 linhas estimadas.
