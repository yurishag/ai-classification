import pytest
from fastapi.testclient import TestClient
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Import the FastAPI app instance
from app.main import app

client = TestClient(app)

def test_app_metadata():
    assert app.title == "LLM Classifier Service"
    assert app.description == "Serve text classification tasks via LLMs"
    assert app.version == "1.0.0"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redocs"

def test_docs_endpoints():
    response = client.get("/docs")
    assert response.status_code == 200
    response = client.get("/redocs")
    assert response.status_code == 200

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    # Prometheus metrics are plain-text
    assert "text/plain" in response.headers["content-type"]

def test_rate_limiter_and_exception_handler():
    # Limiter must be attached to app.state
    assert hasattr(app.state, "limiter")
    assert app.state.limiter is not None
    # The RateLimitExceeded handler must be registered
    assert RateLimitExceeded in app.exception_handlers
    assert app.exception_handlers[RateLimitExceeded] == _rate_limit_exceeded_handler

def test_middleware_setup():
    # SlowAPIMiddleware should be in the middleware stack
    assert any(m.cls is SlowAPIMiddleware for m in app.user_middleware)

def test_classify_router_included():
    # Verify that at least one route is mounted under the /classify prefix
    classify_routes = [route for route in app.routes if route.path.startswith("/classify")]
    assert classify_routes, "No routes found under /classify"
