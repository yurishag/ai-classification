"""
app/services/llm_client.py

Returns an OpenAI LLM client
"""

import os
from openai import OpenAI
from app.config import LLMConfig
from app.utils import logger


def get_llm_client(cfg: LLMConfig) -> OpenAI:
    if cfg.provider.lower() != 'openai':
        raise NotImplementedError(f"Provider {cfg.provider} not yet supported")
    api_key = os.getenv(cfg.api_key_env)
    if not api_key:
        logger.error(f"Env var {cfg.api_key_env} not set")
        raise RuntimeError("LLM API key is missing")
    return OpenAI(api_key=api_key)