from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = ""
    database_url: str = ""
    api_v1_prefix: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
