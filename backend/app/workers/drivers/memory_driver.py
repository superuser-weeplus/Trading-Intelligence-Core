import asyncio
import logging
from app.workers.base_worker import BaseQueueDriver
from app.workers.jobs import execute_job

logger = logging.getLogger("app.workers.drivers.memory")

class MemoryQueueDriver(BaseQueueDriver):
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None
        self.running = False

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.worker_task = asyncio.create_task(self._worker_loop())
        logger.info("In-memory Asyncio Queue Worker started.")

    async def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("In-memory Asyncio Queue Worker stopped.")

    async def enqueue(self, job_name: str, payload: dict) -> None:
        await self.queue.put((job_name, payload))
        logger.info(f"Job enqueued: {job_name}")

    async def _worker_loop(self):
        while self.running:
            try:
                job_name, payload = await self.queue.get()
                try:
                    await execute_job(job_name, payload)
                except Exception as e:
                    logger.error(f"Error executing job '{job_name}': {e}", exc_info=True)
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(1)
