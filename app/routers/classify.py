"""
app/routers/classify.py

FastAPI router that exposes a single POST endpoint for running text-classification "tasks" via an LLM
with built-in rate limiting and error handling.
"""

from fastapi import APIRouter, HTTPException, Request
from app.config import load_config, settings
from app.models import ClassificationRequest, ClassificationResponse
from app.services.llm_client import get_llm_client
from app.utils import logger
from app.rate_limiter import limiter

router = APIRouter()

@router.post("/{task_name}", response_model=ClassificationResponse)
@limiter.limit(settings.rate_limit.default)
async def classify(request: Request, task_name: str, req: ClassificationRequest):
    cfg = load_config()
    if task_name not in cfg.tasks:
        logger.warning(f"Unknown task: {task_name}")
        raise HTTPException(status_code=404, detail="Task not found")
    task_cfg = cfg.tasks[task_name]
    prompt = task_cfg.prompt_template
    if task_cfg.classes:
        prompt = prompt.replace("{{ classes }}", ", ".join(task_cfg.classes))
    prompt += req.text
    client = get_llm_client(cfg.llm)
    try:
        resp = client.chat.completions.create(
            model=cfg.llm.model,
            temperature=cfg.llm.temperature,
            max_tokens=cfg.llm.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        content = resp.choices[0].message.content.strip()
        return ClassificationResponse(
            task=task_name,
            label=content,
            raw=resp
        )
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail="LLM service error")