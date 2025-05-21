import pytest
import logging

from app.config import load_config, Settings, TaskConfig

def pytest_configure(config):
    
    logging.getLogger().setLevel(logging.DEBUG)

@pytest.fixture(autouse=True)
def clear_load_config_cache():
    """Clear the lru_cache before and after each test to isolate caching behavior."""
    load_config.cache_clear()
    yield
    load_config.cache_clear()


def write_yaml_file(path, data: str):
    path.write_text(data)


def test_load_config_success(tmp_path):
    
    cfg_file = tmp_path / "config.yaml"
    yaml_content = """
llm:
  provider: openai
  model: test-model
  temperature: 0.5
  max_tokens: 128
  api_key_env: TEST_API_KEY

tasks:
  task1:
    type: type1
    prompt_template: template1
    classes:
      - A
      - B

server:
  host: 127.0.0.1
  port: 8080

rate_limit:
  default: 10/m
  redis_url: redis://localhost:6379
"""
    write_yaml_file(cfg_file, yaml_content)

    cfg = load_config(str(cfg_file))

    
    assert isinstance(cfg, Settings)
    
    assert cfg.llm.provider == "openai"
    assert cfg.llm.model == "test-model"
    assert cfg.llm.temperature == 0.5
    assert cfg.llm.max_tokens == 128
    assert cfg.llm.api_key_env == "TEST_API_KEY"
    
    assert "task1" in cfg.tasks
    task = cfg.tasks["task1"]
    assert isinstance(task, TaskConfig)
    assert task.type == "type1"
    assert task.prompt_template == "template1"
    assert task.classes == ["A", "B"]
    
    assert cfg.server.host == "127.0.0.1"
    assert cfg.server.port == 8080
    
    assert cfg.rate_limit.default == "10/m"
    assert cfg.rate_limit.redis_url == "redis://localhost:6379"


def test_load_config_file_not_found(tmp_path, caplog):

    missing = tmp_path / "no_such_config.yaml"
    caplog.set_level(logging.ERROR)
    with pytest.raises(FileNotFoundError):
        load_config(str(missing))

    assert "Configuration file not found at" in caplog.text


def test_load_config_parse_error(tmp_path, caplog):

    bad_file = tmp_path / "bad.yaml"
    write_yaml_file(bad_file, ":- invalid yaml content\n")
    caplog.set_level(logging.ERROR)
    with pytest.raises(Exception):
        load_config(str(bad_file))
    assert "Failed to parse configuration" in caplog.text


def test_taskconfig_default_classes(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    yaml_content = """
llm:
  provider: openai
  model: test
  temperature: 0.0
  max_tokens: 64
  api_key_env: KEY

tasks:
  task1:
    type: type1
    prompt_template: template-only

server:
  host: 0.0.0.0
  port: 8000

rate_limit:
  default: 100/h
  redis_url: redis://localhost:6379
"""
    write_yaml_file(cfg_file, yaml_content)

    cfg = load_config(str(cfg_file))
    task = cfg.tasks.get("task1")
    assert isinstance(task, TaskConfig)
    assert task.classes == []


def test_load_config_caching(tmp_path, monkeypatch):

    cfg_file = tmp_path / "config.yaml"
    yaml_content = """
llm:
  provider: openai
  model: caching-test
  temperature: 0.0
  max_tokens: 10
  api_key_env: KEY

server:
  host: 0.0.0.0
  port: 8000

rate_limit:
  default: 1/s
  redis_url: redis://localhost
"""
    write_yaml_file(cfg_file, yaml_content)

    import app.config as config
    original_safe_load = config.yaml.safe_load
    call_count = {"count": 0}

    def fake_safe_load(stream):
        call_count["count"] += 1
        return original_safe_load(stream)

    monkeypatch.setattr(config.yaml, "safe_load", fake_safe_load)

    cfg1 = load_config(str(cfg_file))
    cfg2 = load_config(str(cfg_file))

    assert call_count["count"] == 1, "yaml.safe_load should be called only once due to caching"
    assert cfg1 is cfg2, "load_config should return the same cached instance"
