import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_password: str
    db_name: str
    db_host: str
    db_port: int
    db_username: str
    port: int
    app_env: str = "development"
    pokeapi_url: str
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"))
    db_ssl: bool = False


settings = Settings()
