from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Text-to-SQL Enterprise"
    debug: bool = False

    database_url: str = "sqlite:///./text2sql.db"
    chroma_persist_dir: str = "./chroma_db"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_api_key: str = ""

    safe_mode: bool = True
    max_rows: int = 500
    query_timeout_seconds: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
