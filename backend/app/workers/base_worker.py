from abc import ABC, abstractmethod

class BaseQueueDriver(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Starts the worker runner loop."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stops the worker runner loop."""
        pass

    @abstractmethod
    async def enqueue(self, job_name: str, payload: dict) -> None:
        """Enqueues a job for execution."""
        pass
