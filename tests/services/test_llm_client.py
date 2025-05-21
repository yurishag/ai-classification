import pytest
from app.config import LLMConfig


class DummyOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key

@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MY_CUSTOM_KEY", raising=False)
    yield

def test_success_returns_llm_client(monkeypatch):

    monkeypatch.setenv("OPENAI_API_KEY", "supersecret")
    cfg = LLMConfig
