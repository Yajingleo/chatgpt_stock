"""Custom logging handler for SSE streaming"""

import logging


class StreamingLogHandler(logging.Handler):
    """Custom log handler that captures logs for SSE streaming"""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        try:
            msg = self.format(record)
            self.callback(msg)
        except Exception:
            pass
