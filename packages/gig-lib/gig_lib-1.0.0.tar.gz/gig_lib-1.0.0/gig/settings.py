# gig/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    public_key_path: str
    algorithm: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix=""
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_public_key() -> bytes:
    """
    Lee y cachea la clave pública desde el fichero PEM.
    """
    settings = get_settings()
    path = settings.public_key_path
    if not os.path.isfile(path):
        raise RuntimeError(f"Public key file not found: {path}")
    with open(path, "rb") as f:
        return f.read()
