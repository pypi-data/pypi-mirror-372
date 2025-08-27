from functools import cache

from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="beemo_")

    pages_dir: DirectoryPath
    posts_dir: DirectoryPath
    static_dir: DirectoryPath
    templates_dir: DirectoryPath
    output_dir: DirectoryPath


@cache
def get_settings() -> Settings:
    return Settings()
