import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_client import get_llm_client as real_get_client
from app.config import load_config

# Dummy LLM client and response for testing
def dummy_response_factory(label):
    class DummyMessage:
        def __init__(self, content):
            self.content = content

    class DummyChoice:
        def __init__(self, message):
            self.message = message

    class DummyResp:
        def __init__(self, label):
            self.choices = [DummyChoice(DummyMessage(label))]

    return DummyResp(label)

class DummyClient:
    def __init__(self, label):
        self.chat = self
        self.completions = self
        self._label = label

    def create(self, **kwargs):
        return dummy_response_factory(self._label)

@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    # For sentiment tasks, return "Positive"; for product_category, "Home"
    def fake_get_llm_client(cfg):
        if cfg.model == load_config().llm.model and 'sentiment' in cfg.tasks:
            return DummyClient("Positive")
        return DummyClient("Home")

    monkeypatch.setattr('app.services.llm_client.get_llm_client', fake_get_llm_client)

client = TestClient(app)

def test_sentiment_classification():
    resp = client.post(
        "/classify/sentiment",
        json={"text": "I loved this movie!"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['task'] == 'sentiment'
    assert data['label'] == 'Positive'


def test_product_category_classification():
    resp = client.post(
        "/classify/product_category",
        json={"text": "This blender works great for smoothies."}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['task'] == 'product_category'
    assert data['label'] == 'Home'


def test_unknown_task_returns_404():
    resp = client.post(
        "/classify/unknown_task",
        json={"text": "test"}
    )
    assert resp.status_code == 404