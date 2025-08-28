from __future__ import annotations

import asyncio
from asyncio import Task

from .exception import PoolStartedError


class Job: ...


class WorkerPool:
    """WorkerPool is a highly configurable asyncio worker pool."""

    def __init__(self, max_workers: int, worker_scale_duration: int = 0) -> None:
        self.max_workers = max(0, max_workers)
        self.worker_scale_duration = worker_scale_duration
        self.q = asyncio.Queue[Job](maxsize=0)
        self._shutdown = asyncio.Event()
        self._started = False
        self._worker_tasks: list[Task] = []

    def start(self) -> None:
        """start starts the worker pool, creating upto max_workers number of
        tasks monitoring the internal queue."""
        if self._started:
            raise PoolStartedError("pool is already running, cannot be started twice")
        self._started = True
        for worker_id in range(self.max_workers):
            worker = asyncio.create_task(self._worker(worker_id))
            self._worker_tasks.append(worker)

    async def submit(self, task: Task) -> None: ...

    async def submit_wait(self, task: Task) -> None: ...

    async def stop(self) -> None: ...

    async def drain(self) -> None: ...

    async def throttle(self, duration: int) -> None: ...

    async def __enter__(self) -> WorkerPool:
        self.start()
        return self

    async def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()

    async def _worker(self, worker_id: int) -> None:
        """_worker attempts to read elements from the queue internally to process
        the task until the shutdown event is triggered."""
        while self._shutdown.is_set():
            ...


class Worker:
    """Worker encapsulates a coroutine that can receive tasks to execute."""

    def __init__(self, q: asyncio.Queue) -> None:
        self.q = q
