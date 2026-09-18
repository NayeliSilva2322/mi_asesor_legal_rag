import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = (
    "Eres un asesor legal virtual especializado en el sistema judicial peruano. "
    "Responde en espanol, de forma clara y precisa, basandote unicamente en el "
    "contexto proporcionado. Si el contexto no contiene la respuesta, dilo "
    "explicitamente en lugar de inventar informacion."
)


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Contexto:\n{context}\n\n"
        f"Pregunta: {question}\n"
        f"Respuesta:"
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Llama a un endpoint de generacion de texto compatible con TGI."""
    prompt = build_prompt(question, context_chunks)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": settings.llm_max_new_tokens,
            "temperature": settings.llm_temperature,
            "repetition_penalty": settings.llm_repetition_penalty,
            "return_full_text": False,
        },
    }
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(f"{settings.llm_base_url}/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("generated_text", "").strip()
