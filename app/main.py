import uvicorn
from fastapi import FastAPI
from app.config import load_config
from app.routers.classify import router as classify_router
from app.utils import setup_logging
from dotenv import load_dotenv

load_dotenv() 

# Setup logging
setup_logging()

# Load configuration
cfg = load_config()

# Initialize FastAPI
app = FastAPI(
    title="LLM Classifier Service",
    description="Serve text classification tasks via LLMs",
    version="1.0.0"
)

# Include routers
app.include_router(classify_router, prefix="/classify")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=cfg.server.host,
        port=cfg.server.port,
        log_level="info"
    )