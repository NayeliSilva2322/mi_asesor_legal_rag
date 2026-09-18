from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    database_url: str = "postgresql+psycopg://asesor:asesor@localhost:5432/asesor_legal"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    embedding_dim: int = 768

    # Retrieval / chunking (mismos defaults que el notebook original)
    chunk_size: int = 500
    chunk_overlap: int = 20
    top_k: int = 4

    # Backend del LLM (endpoint compatible con TGI / OpenAI)
    llm_base_url: str = "http://llm:80"
    model_id: str = "NAYEIRN23/mi-asesor-legal"
    hf_token: str | None = None
    llm_max_new_tokens: int = 512
    llm_temperature: float = 0.3
    llm_repetition_penalty: float = 1.1

    # Ingesta
    data_dir: str = "/app/data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
