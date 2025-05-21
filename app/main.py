import uvicorn
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
from prometheus_client import make_asgi_app

from app.config import load_config
from app.routers.classify import router as classify_router
from app.utils import setup_logging
from app.rate_limiter import limiter

load_dotenv() 

# Setup logging
setup_logging()

# Load configuration
cfg = load_config()

# Initialize FastAPI
app = FastAPI(
    title="LLM Classifier Service",
    description="Serve text classification tasks via LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redocs"
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(classify_router, prefix="/classify")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=cfg.server.host,
        port=cfg.server.port,
        log_level="info"
    )