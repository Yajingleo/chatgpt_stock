"""Application service for curated analysis memory."""

from typing import Optional

from agent.domain import AnalysisRun


class AnalysisMemoryService:
    def __init__(self, store, enabled: bool = True, default_limit: int = 10):
        self.store = store
        self.enabled = enabled
        self.default_limit = default_limit

    def remember(self, run: AnalysisRun) -> Optional[str]:
        if not self.enabled or (not run.sentiment and not run.recommendations):
            return None
        return self.store.save(run)

    def search(self, ticker=None, limit=None):
        return self.store.search(ticker=ticker, limit=limit or self.default_limit) if self.enabled else []

    def get(self, run_id: str):
        run = self.store.get(run_id) if self.enabled else None
        return run.to_dict() if run else None
