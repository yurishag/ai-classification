import os
import yaml
import pytest
from app.config import load_config

def test_loads_yaml_and_env(tmp_path, monkeypatch):
    cfg_data = {
        "llm": { "provider":"openai", "model":"m", "temperature":0, "max_tokens":10, "api_key_env":"OPENAI_API_KEY" },
        "tasks": {},
        "server": {"host":"0.0.0.0","port":8000},
        "rate_limit": {"default":"5/minute","redis_url":"REDIS_URL"}
    }
    f = tmp_path / "cfg.yaml"
    f.write_text(yaml.dump(cfg_data))

    monkeypatch.setenv("OPENAI_API_KEY", "abc")
    monkeypatch.setenv("REDIS_URL", "redis://x")

    settings = load_config(str(f))
    assert settings.llm.model == "m"
    assert os.getenv(settings.llm.api_key_env) == "abc"
    assert settings.rate_limit.default == "5/minute"
    assert settings.rate_limit.redis_url == "REDIS_URL"

def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "nothing.yaml"))
