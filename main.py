import os
import sys

import requests
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager
from strands_tools import current_time

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "Você é um assistente em um chat de terminal. Responda sempre em "
    "português (pt-BR), de forma concisa e amigável. Quando o usuário "
    "perguntar sobre o clima ou tempo de um lugar, use a ferramenta "
    "get_weather. Quando perguntarem a data ou hora atual, use a "
    "ferramenta current_time. Para demais perguntas, responda com seu "
    "conhecimento. Se uma cidade não for encontrada, sugira verificar "
    "o nome."
)


@tool
def get_weather(city: str, country_code: str = "") -> dict:
    """Obtém o clima atual de uma cidade via OpenWeatherMap.

    Args:
        city: Nome da cidade (ex.: "São Paulo").
        country_code: Código ISO do país para desambiguar (ex.: "BR"). Opcional.
    """
    query = f"{city},{country_code}" if country_code else city
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": query,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "pt_br",
            },
            timeout=10,
        )
    except requests.RequestException:
        return {"erro": "Falha ao consultar o serviço de clima. Verifique sua conexão."}

    if resp.status_code == 404:
        return {"erro": f"Cidade '{city}' não encontrada. Verifique o nome."}
    if resp.status_code != 200:
        return {"erro": "Falha ao consultar o serviço de clima."}

    data = resp.json()
    return {
        "cidade": f"{data['name']}, {data['sys'].get('country', '')}".rstrip(", "),
        "descricao": data["weather"][0]["description"],
        "temperatura_c": data["main"]["temp"],
        "sensacao_termica_c": data["main"]["feels_like"],
        "umidade_pct": data["main"]["humidity"],
        "vento_ms": data["wind"]["speed"],
    }


def check_env() -> None:
    missing = [
        name
        for name in ("OPENAI_API_KEY", "OPENWEATHER_API_KEY")
        if not os.getenv(name)
    ]
    if missing:
        print(f"Erro: variável(is) de ambiente ausente(s): {', '.join(missing)}.")
        print("Preencha o arquivo .env (veja .env.example) e execute novamente.")
        sys.exit(1)


def create_agent() -> Agent:
    model = OpenAIModel(
        client_args={"api_key": OPENAI_API_KEY},
        model_id=OPENAI_MODEL,
    )
    session_manager = FileSessionManager(
        session_id="chat_clima",
        storage_dir="./sessions",
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_weather, current_time],
        session_manager=session_manager,
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    check_env()
    agent = create_agent()

    print("Agente de clima iniciado. Digite 'sair' para encerrar.")
    print("(A conversa fica salva em ./sessions — apague a pasta para recomeçar.)\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAgente: Até logo!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("Agente: Até logo!")
            break

        try:
            response = agent(user_input)
            print(f"Agente: {response}\n")
        except Exception as exc:
            print(f"Agente: Desculpe, ocorreu um erro: {exc}\n")


if __name__ == "__main__":
    main()
