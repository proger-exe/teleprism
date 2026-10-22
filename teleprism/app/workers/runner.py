"""Background worker runner."""

import asyncio
from collections.abc import Callable, Coroutine
from contextlib import suppress
from typing import Any


class WorkerRunner:
    """Start and stop background worker coroutines."""

    def __init__(self) -> None:
        """Initialize task list."""

        self.tasks: list[asyncio.Task[None]] = []

    def add(self, worker: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """Schedule a worker coroutine."""

        self.tasks.append(asyncio.create_task(worker()))

    async def stop(self) -> None:
        """Cancel all running worker tasks."""

        for task in self.tasks:
            task.cancel()
        for task in self.tasks:
            with suppress(asyncio.CancelledError):
                await task
