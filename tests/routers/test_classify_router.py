# tests/routers/test_classify_router.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import app.services.llm_client as llm_mod

class FakeClient:
    async def create(self, *args, **kwargs):
        class R: choices = [{"message": {"content": "MOCK"}}]
        return R()
    @property
    def chat(self): return self
    @property
    def completions(self): return self

@pytest.fixture(autouse=True)
def stub_llm(monkeypatch):
    monkeypatch.setattr(llm_mod, "get_llm_client", lambda cfg: FakeClient())

client = TestClient(app)

def test_classify_endpoint_returns_mock():
    r = client.post("/classify/sentiment", json={"text":"hi"})
    assert r.status_code == 200
    assert r.json()["label"] == "MOCK"
