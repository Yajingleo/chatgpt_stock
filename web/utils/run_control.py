"""Cancellable chat runs, so the UI can stop a query that is still working."""

import asyncio
import threading
import uuid
from typing import Awaitable, Callable, Dict, Optional


class RunCancelled(Exception):
    """Raised by ``RunControl.execute`` when the run was stopped."""


class RunControl:
    """One in-flight chat query that another thread can stop."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.cancelled = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None

    def cancel(self) -> None:
        self.cancelled.set()
        loop, task = self._loop, self._task
        if loop is not None and task is not None:
            try:
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:  # loop already closed
                pass

    def execute(self, coro_factory: Callable[[], Awaitable]):
        """Run the coroutine on a worker thread and wait for it or for a cancel.

        A blocking call inside the agent can't be interrupted, so on cancel the
        worker is abandoned (it is a daemon thread) instead of joined.
        """
        done = threading.Event()
        outcome: Dict[str, object] = {}

        async def main():
            self._loop = asyncio.get_running_loop()
            self._task = asyncio.current_task()
            return await coro_factory()

        def worker():
            try:
                outcome['value'] = asyncio.run(main())
            except BaseException as error:  # includes CancelledError
                outcome['error'] = error
            finally:
                done.set()

        threading.Thread(target=worker, daemon=True).start()
        while not done.wait(0.1):
            if self.cancelled.is_set():
                raise RunCancelled()
        if self.cancelled.is_set():
            raise RunCancelled()
        if 'error' in outcome:
            raise outcome['error']
        return outcome['value']


class RunRegistry:
    """Tracks active runs by id so a stop request can find them."""

    def __init__(self):
        self._runs: Dict[str, RunControl] = {}
        self._lock = threading.Lock()

    def start(self) -> RunControl:
        control = RunControl(uuid.uuid4().hex)
        with self._lock:
            self._runs[control.run_id] = control
        return control

    def finish(self, control: RunControl) -> None:
        with self._lock:
            self._runs.pop(control.run_id, None)

    def stop(self, run_id: str) -> bool:
        with self._lock:
            control = self._runs.get(run_id)
        if control is None:
            return False
        control.cancel()
        return True
