### 1. Framework: FastAPI
Chosen for its high-performance async support, automatic OpenAPI spec generation, and ease of dependency injection.

### 2. Configuration: Pydantic + YAML + .env

- config.yaml holds task definitions, prompt templates, server settings, and rate-limit defaults.

- .env stores secrets (API keys, Redis URL, OTLP endpoint).

- Pydantic BaseSettings merges both, with env_nested_delimiter="_" to map nested fields.

### 3. LLM Client Abstraction

- Factory (get_llm_client) selects between the LLM (OpenAI) via provider: in config. This allows the addition of other models such as Anthropic or Gemini.


### 4. Prompt-Driven, Configurable Tasks

- Supports any number of classification tasks by templating prompts in YAML.

- Encourages adding new tasks (datasets) without code changes.

### 5. Async I/O & Concurrency

- Endpoints and LLM calls are fully async to maximize throughput under I/O wait.

### 6. Rate Limiting: SlowAPI + Redis

- Global per-IP default (“10/minute”) defined in config.

- Backed by Redis for shared counters across replicas.

### 7. Observability

- Metrics: Prometheus client mounted at /metrics for latency, QPS, error rates.


### 8. Logging

- Structured, JSON-style logs with request/thread IDs (via a central logger helper).


### 9. Testing

- Unit tests: pytest + pytest-asyncio for config loader, client factory, utils.

- Integration tests: FastAPI’s TestClient with monkeypatch-based LLM stubs to validate endpoints.


### 11. CI/CD Pipeline

- GitHub Actions (or equivalent) to lint (flake8/isort), type-check (mypy), test, build/publish Docker images, and deploy to staging/production.

### 12. Security & Secrets Management

- Secrets injected via environment variables (or external secret stores).

- No secrets in code or config files; all inputs validated by Pydantic.

### 13. Health & Readiness Probes

- Planned /health and /ready endpoints for orchestrator liveness/readiness checks (can be added as soon as needed).