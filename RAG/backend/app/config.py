from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "meetings"
    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "llama3"
    # openai_api_key: str = ""
    top_k: int = 10
    score_threshold: float = 0.2
    sse_chunk_delay: float = 0.01
    class Config:
        env_file = ".env"

settings = Settings()
