from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Project Management API"
    database_url: str = "sqlite:///./sql_app.db"
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
