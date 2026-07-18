from app.config import settings
from app.workers.drivers.memory_driver import MemoryQueueDriver
from app.workers.drivers.redis_driver import RedisQueueDriver

# Instantiate active driver based on settings configuration
if settings.QUEUE_DRIVER.lower() == "redis":
    worker = RedisQueueDriver(redis_url=settings.REDIS_URL)
else:
    worker = MemoryQueueDriver()
