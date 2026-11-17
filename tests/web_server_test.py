"""Regression coverage for shared streaming and ordinary chat processing."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from web import server


class ChatProcessingTest(unittest.TestCase):
    def setUp(self):
        self.handler = object.__new__(server.StockChatHandler)
        self.handler.agent = SimpleNamespace(run=AsyncMock())
        self.handler.chat_history = []

    def process(self, message, callback):
        with patch.object(server, 'STOCK_AGENT_AVAILABLE', True):
            return asyncio.run(self.handler._process_user_message(message, callback))

    def test_help_reaches_the_agent_in_both_modes(self):
        self.handler.agent.run.return_value = {'success': True, 'answer': 'Capabilities'}
        for callback in (None, lambda *args: None):
            for message in ('help', '/help', '?'):
                self.assertEqual(self.process(message, callback), 'Capabilities')
                self.handler.agent.run.assert_awaited_with(message, history=[], progress_callback=callback)

    def test_answer_and_callback_in_both_modes(self):
        self.handler.agent.run.return_value = {'success': True, 'answer': 'Analysis'}
        for callback in (None, lambda *args: None):
            self.assertEqual(self.process('Analyze QCOM', callback), 'Analysis')
            kwargs = {'progress_callback': callback}
            self.handler.agent.run.assert_awaited_with('Analyze QCOM', history=[], **kwargs)

    def test_failures_are_consistent_in_both_modes(self):
        for callback in (None, lambda *args: None):
            self.handler.agent.run.return_value = {'success': False, 'error': 'Unavailable'}
            self.assertEqual(self.process('Analyze QCOM', callback), '❌ Analysis failed: Unavailable')
            self.handler.agent.run.side_effect = RuntimeError('Offline')
            self.assertIn('Offline', self.process('Analyze QCOM', callback))
            self.handler.agent.run.side_effect = None


if __name__ == '__main__':
    unittest.main()
