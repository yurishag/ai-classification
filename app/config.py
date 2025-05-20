import os
import yaml
import logging
from functools import lru_cache
from pydantic import BaseSettings, Field

tasks_default = {}

class TaskConfig(BaseSettings):
    type: str
    prompt_template: str
    classes: list[str] = Field(default_factory=list)

class LLMConfig(BaseSettings):
    provider: str = "openai"
    model: str
    temperature: float = 0.0
    max_tokens: int = 64
    api_key_env: str

class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000

class Config(BaseSettings):
    llm: LLMConfig
    tasks: dict[str, TaskConfig] = tasks_default
    server: ServerConfig

    class Config:
        env_prefix = ""
        env_file = ".env"

@lru_cache()
def load_config(path: str = "config.yaml") -> Config:
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return Config(**data)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {path}")
        raise
    except Exception as e:
        logging.exception("Failed to parse configuration")
        raise