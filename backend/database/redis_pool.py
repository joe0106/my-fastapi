import redis
from backend.setting.config import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool.from_url(settings.redis_url)