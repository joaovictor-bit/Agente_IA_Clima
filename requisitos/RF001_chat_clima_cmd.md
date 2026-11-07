# REQUISITO FUNCIONAL — RF-001
## Chat Interativo via CMD — Agente de Clima

## 1. Identificação

- **Código:** RF-001
- **Nome:** Chat interativo de console com agente de clima
- **Versão:** 1.0
- **Data:** 07/11/2026
- **Status:** Aprovado para implementação
- **Prioridade:** Alta

## 2. Objetivo

Construir um chat interativo executado no terminal (CMD/PowerShell) que
funcione como um agente de IA simples. O agente deve conversar livremente
com o usuário e, quando solicitado, informar o clima atual de um local
(cidade) indicado na mensagem.

## 3. Escopo

**DENTRO do escopo:**

- Interface de texto via linha de comando (sem interface gráfica/web).
- Agente construído com o framework Strands Agents (SDK open-source da AWS).
- OpenAI como provedor do modelo de linguagem (LLM).
- Ferramenta (tool) de clima que consulta a API do OpenWeatherMap.
- Conversação em português (pt-BR).

**FORA do escopo:**

- Interface gráfica, web ou mobile.
- Persistência do histórico em banco de dados ou arquivo
  (o histórico existe apenas em memória durante a sessão).
- Previsão para dias futuros (somente clima atual).
- Múltiplos usuários simultâneos ou uso em rede.

## 4. Descrição do Fluxo Principal

1. O usuário executa o script Python no terminal.
2. O programa exibe uma mensagem de boas-vindas e o prompt de entrada.
3. O usuário digita uma mensagem qualquer (ex.: "Como está o clima
   em São Paulo?" ou "Bom dia!").
4. O agente (LLM via Strands) interpreta a mensagem:
   - Se for um pedido de clima, o agente identifica a cidade e chama
     a ferramenta de clima.
   - A ferramenta consulta o OpenWeatherMap e retorna os dados.
   - O agente formata a resposta em linguagem natural.
   - Se não for pedido de clima, o agente responde normalmente com
     o conhecimento do modelo.
5. A resposta é exibida no terminal e o prompt reaparece (loop).
6. O usuário encerra digitando "sair" (ou "exit"/"quit") ou Ctrl+C.

## 5. Requisitos Funcionais

- **RF-01:** O sistema deve exibir um prompt no terminal aguardando a
  entrada do usuário, em loop, até que ele decida sair.

- **RF-02:** O sistema deve encerrar a sessão quando o usuário digitar
  "sair", "exit" ou "quit" (sem distinção de maiúsculas), ou ao
  pressionar Ctrl+C, exibindo uma mensagem de despedida.

- **RF-03:** O sistema deve manter o contexto da conversa em memória
  durante a sessão, permitindo perguntas de acompanhamento
  (ex.: "e em Recife?" após perguntar por outra cidade).

- **RF-04:** O sistema deve fornecer uma ferramenta (tool) de clima ao
  agente, que receba como parâmetro o nome da cidade (e
  opcionalmente o país) e retorne:
  - Descrição do clima (ex.: céu limpo, nublado, chuva)
  - Temperatura atual em graus Celsius
  - Sensação térmica
  - Umidade relativa do ar

  (dados obtidos da API OpenWeatherMap, endpoint de clima atual,
  com `units=metric` e `lang=pt_br`).

- **RF-05:** O agente deve decidir automaticamente quando chamar a
  ferramenta de clima, sem que o usuário use comandos especiais.

- **RF-06:** Mensagens que não sejam sobre clima devem ser respondidas
  normalmente pelo modelo, sem chamar a ferramenta.

- **RF-07:** Se a cidade não for encontrada, o sistema deve informar ao
  usuário de forma amigável e sugerir verificar o nome.

- **RF-08:** Em caso de falha na comunicação com as APIs (sem internet,
  chave inválida, limite excedido), o sistema deve exibir uma
  mensagem de erro clara, sem encerrar o programa.

## 6. Requisitos Não Funcionais

- **RNF-01:** Linguagem Python 3.10 ou superior.

- **RNF-02:** Simplicidade: o projeto deve ser mínimo — idealmente um
  único arquivo principal (ex.: `main.py`), sem abstrações
  desnecessárias.

- **RNF-03:** Dependências (gerenciadas via `pip`/`requirements.txt`):
  - `strands-agents` — framework do agente
  - `openai` ou provider equivalente do Strands
  - `requests` ou `httpx` — chamada ao OpenWeatherMap
  - `python-dotenv` — carregar variáveis de ambiente

- **RNF-04:** Chaves de API devem ser lidas de variáveis de ambiente
  (arquivo `.env`, não commitado), nunca escritas no código:
  - `OPENAI_API_KEY`
  - `OPENWEATHER_API_KEY`

- **RNF-05:** Todas as mensagens exibidas ao usuário devem estar em
  português (pt-BR).

- **RNF-06:** O sistema deve funcionar no Windows (CMD e PowerShell).

## 7. Pré-requisitos

- Python 3.10+ instalado e no PATH.
- Chave de API da OpenAI válida.
- Chave de API do OpenWeatherMap válida (plano gratuito é suficiente).
- Acesso à internet.

## 8. Critérios de Aceite

- **CA-01:** Ao executar `python main.py`, o chat inicia e aguarda entrada.
- **CA-02:** Perguntando "Qual o clima no Rio de Janeiro?", o agente chama
  a ferramenta e responde com temperatura, descrição e umidade.
- **CA-03:** Perguntas genéricas (ex.: "Me conte uma curiosidade") são
  respondidas sem chamar a ferramenta de clima.
- **CA-04:** Uma cidade inexistente gera mensagem amigável, sem crash.
- **CA-05:** Digitar "sair" encerra o programa com mensagem de despedida.
- **CA-06:** Sem chave de API configurada, o programa avisa o que está
  faltando ao iniciar, em vez de falhar com erro técnico.
- **CA-07:** Nenhuma chave de API aparece no código-fonte.

## 9. Exemplo de Uso

```text
> python main.py
Agente de clima iniciado. Digite 'sair' para encerrar.

Você: Oi! Como está o clima em Fortaleza?
Agente: Em Fortaleza está céu limpo, 31°C (sensação de 34°C),
        umidade de 62%.

Você: e em São Paulo?
Agente: Em São Paulo está nublado, 19°C (sensação de 18°C),
        umidade de 88%.

Você: sair
Agente: Até logo!
```

## 10. Observações

- "AWS Strands" refere-se ao Strands Agents, SDK open-source de
  agentes mantido pela AWS (não requer conta AWS; neste projeto ele
  atua apenas como framework do agente, com a OpenAI como modelo).
- O plano gratuito do OpenWeatherMap permite até ~1.000 chamadas/dia,
  suficiente para o uso proposto.
