<!-- Prerequisites:
Python
OpenAI API Key

1. Clone/copy the repo:

git clone https://github.com/yurishag/ai-classification.git
cd ai-classification

2. Create a .env in the project root with:
OPENAI_API_KEY="sk-...your key..."

3. Install dependencies into a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-cache-dir -r requirements.txt

4. Run with Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

5. Hit the API:
- curl -X POST http://localhost:8000/classify/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text":"I loved this movie!"}'

  -->


# LLM Classifier Microservice

A high-performance, scalable Python microservice that exposes prompt-engineered text classification tasks via a FastAPI HTTP API.  
Built for production readiness with configuration-driven LLM support, rate-limiting, caching, metrics, tracing, Docker, and full test coverage.

---

## Table of Contents

1. [Features](#features)  
2. [File Structure](#file-structure)  
3. [Prerequisites](#prerequisites)  
4. [Getting Started](#getting-started)  
   - [Clone & Install](#clone--install)  
   - [Configuration](#configuration)  
   - [Running Locally](#running-locally)  
   - [Docker & Docker Compose](#docker--docker-compose)  
5. [API Reference](#api-reference)  
6. [Metrics & Tracing](#metrics--tracing)  
6. [Benchmarking](#benchmarking)  
---

## Features

- **Prompt-Driven Classification**  
  - Binary (e.g. sentiment) and multi-class (e.g. product category) tasks  
  - Fully configurable via `config.yaml`  
- **LLM Provider Agnostic**  
  - Built-in support for OpenAI (easy to extend to AWS Bedrock, Anthropic, Gemini)  
- **Production-Ready**  
  - Async FastAPI + Uvicorn workers  
  - Built-in rate-limiting (SlowAPI / Redis)  
  - Caching of repeated prompts (LRU)  
  - Structured logging with correlation IDs  
- **Observability**  
  - Prometheus metrics at `/metrics`   

---

## File Structure


```text
llm_classifier_service/
├── app/
│ ├── main.py 
│ ├── config.py 
│ ├── models.py 
│ ├── rate_limiter.py 
│ ├── routers/
│ │ └── classify.py
│ ├── services/
│ │ └── llm_client.py 
│ └── utils.py 
│
├── tests/
│ ├── test_config.py
│ ├── test_llm_client.py
│ ├── test_utils.py
│ └── routers/
│ └── test_classify_router.py
│
├── scripts/
│ └── benchmark.py 
│
├── docs/
│ ├── architecture.md
│ ├── design_decisions.md
│ └── usage.md
│
├── config.yaml 
├── requirements.txt 
├── Dockerfile
├── docker-compose.yml
├── .env.example # Sample environment variables
├── pytest.ini
└── README.md
```

## Prerequisites
- Python 3.12+
- Redis (optional, for rate-limit)
- An OpenAI API Key


## Getting Started

### Clone and Install
```bash
git clone https://github.com/yurishag/ai-classification.git

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell

# Install packages
pip install --no-cache-dir -r requirements.txt
```

### Configuration

1. Copy .env.example → .env and fill in your secrets:
```ini
OPENAI_API_KEY=sk-…
REDIS_URL=redis://:<PWD>@localhost:6379
```

### Running Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI**: http://localhost:8000/docs

- **ReDoc**: http://localhost:8000/redoc

- **Metrics**: http://localhost:8000/metrics


### Testing the Classification API
1. **Movie Rating**

    URL: POST  http://localhost:8000/classify/movie_rating

    Request Body:
    ```json
    {
      "text": "Jurassic Park is the best movie ever!"
    }
    ```

    Response (200 OK):
     ```json
    {
      "task": "movie_rating",
      "label": "Positive",
      "raw": { /* full LLM response object */ }
    }
    ```

2. **Product Rating**

    URL: POST  http://localhost:8000/classify/product_category

    Request Body:
    ```json
    {
      "text": "This product is amazing and does exactly what it says."
    }
    ```

    Response (200 OK):
     ```json
    {
      "task": "product_category",
      "label": "5",
      "raw": { /* full LLM response object */ }
    }
    ```

**Errors**
- 404 Task not found if task_name unknown
- 429 Too Many Requests if rate-limited
- 500 LLM service error on upstream failure



### Metrics
- **Prometheus**
    - Endpoint: GET /metrics
    - Scrape latency, request counts, error rates, etc.


## Benchmarking
To test the performance of the microservice by measuring latency and throughput.

1. Running Benchmarking script:
```bash
python .\scripts\benchmark.py --url http://localhost:8000/classify/movie_rating --text "This movie is great" --requests 30 --concurrency 10
```