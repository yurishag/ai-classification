import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

from dotenv import load_dotenv
load_dotenv()  

redis_uri = os.getenv(settings.rate_limit.redis_url)
# storage = redis_uri or "memory://"
storage = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit.default],
    storage_uri=storage
)
