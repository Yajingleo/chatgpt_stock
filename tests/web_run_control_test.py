"""Tests for stopping in-flight chat runs."""

import asyncio
import threading
import time
import unittest

from web.utils.run_control import RunCancelled, RunRegistry


class RunControlTest(unittest.TestCase):
    def test_returns_the_coroutine_result(self):
        control = RunRegistry().start()

        async def work():
            return 'answer'

        self.assertEqual(control.execute(work), 'answer')

    def test_propagates_errors(self):
        control = RunRegistry().start()

        async def work():
            raise ValueError('boom')

        with self.assertRaises(ValueError):
            control.execute(work)

    def test_stop_interrupts_a_run_awaiting_io(self):
        registry = RunRegistry()
        control = registry.start()

        async def work():
            await asyncio.sleep(30)

        threading.Timer(0.2, registry.stop, args=(control.run_id,)).start()
        started = time.monotonic()
        with self.assertRaises(RunCancelled):
            control.execute(work)
        self.assertLess(time.monotonic() - started, 5)

    def test_stop_does_not_wait_for_a_blocking_call(self):
        registry = RunRegistry()
        control = registry.start()
        release = threading.Event()

        async def work():
            release.wait(30)  # blocks the event loop, like a hung sync call

        threading.Timer(0.2, registry.stop, args=(control.run_id,)).start()
        started = time.monotonic()
        try:
            with self.assertRaises(RunCancelled):
                control.execute(work)
            self.assertLess(time.monotonic() - started, 5)
        finally:
            release.set()

    def test_stop_unknown_or_finished_run_returns_false(self):
        registry = RunRegistry()
        control = registry.start()
        registry.finish(control)
        self.assertFalse(registry.stop(control.run_id))
        self.assertFalse(registry.stop('missing'))


if __name__ == '__main__':
    unittest.main()
