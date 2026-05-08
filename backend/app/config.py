from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Silver Research Agent"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./silver_data.db"

    # API Keys (set in .env)
    openai_api_key: str = ""
    newsapi_key: str = ""

    # Silver data sources
    mcx_base_url: str = "https://www.mcxindia.com"
    gold_api_key: str = ""  # goldapi.io for live XAG

    # Agent config
    research_model: str = "gpt-4o"
    max_research_depth: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
