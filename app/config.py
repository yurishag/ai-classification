import yaml
import logging
from functools import lru_cache
from pydantic import BaseSettings, Field, BaseModel

tasks_default = {}

class RateLimitConfig(BaseModel):
    default: str
    redis_url: str

class TaskConfig(BaseModel):
    type: str
    prompt_template: str
    classes: list[str] = Field(default_factory=list)

class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str
    temperature: float = 0.0
    max_tokens: int = 64
    api_key_env: str

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class Settings(BaseSettings):
    llm: LLMConfig
    tasks: dict[str, TaskConfig] = tasks_default
    server: ServerConfig
    rate_limit: RateLimitConfig

    class Config:
        env_prefix = ""
        env_file = ".env"
        env_nested_delimiter = "_"


@lru_cache()
def load_config(path: str = "config.yaml") -> Settings:
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return Settings(**data)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {path}")
        raise
    except Exception as e:
        logging.exception("Failed to parse configuration")
        raise


settings = load_config()