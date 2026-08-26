"""Versioned filesystem analysis memory."""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.domain import AnalysisRun


class FileSystemMemoryStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.index_path = self.root / "index.jsonl"
        self._lock = threading.RLock()

    def save(self, run: AnalysisRun) -> str:
        created = datetime.fromisoformat(run.created_at.replace("Z", "+00:00"))
        run_dir = self.root / "runs" / created.strftime("%Y/%m/%d") / run.run_id
        with self._lock:
            run_dir.mkdir(parents=True, exist_ok=True)
            analysis_path = run_dir / "analysis.json"
            self._atomic_write(analysis_path, json.dumps(run.to_dict(), indent=2, sort_keys=True))
            self._atomic_write(run_dir / "summary.md", self._summary(run))
            with self.index_path.open("a", encoding="utf-8") as index:
                index.write(json.dumps(self._record(run, analysis_path)) + "\n")
        return run.run_id

    def get(self, run_id: str) -> Optional[AnalysisRun]:
        for record in self._read_index():
            if record.get("run_id") == run_id and Path(record["path"]).exists():
                return AnalysisRun.from_dict(json.loads(Path(record["path"]).read_text(encoding="utf-8")))
        return None

    def search(self, ticker: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        records = self._read_index()
        if ticker:
            records = [item for item in records if ticker.upper() in item.get("tickers", [])]
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)[:max(1, limit)]

    def _read_index(self) -> List[Dict[str, Any]]:
        if not self.index_path.exists():
            return self._rebuild_index()
        try:
            return [json.loads(line) for line in self.index_path.read_text(encoding="utf-8").splitlines() if line]
        except (json.JSONDecodeError, OSError):
            return self._rebuild_index()

    def _rebuild_index(self) -> List[Dict[str, Any]]:
        records = []
        for path in self.root.glob("runs/*/*/*/*/analysis.json"):
            try:
                run = AnalysisRun.from_dict(json.loads(path.read_text(encoding="utf-8")))
                records.append(self._record(run, path))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
                continue
        if records:
            self.root.mkdir(parents=True, exist_ok=True)
            self._atomic_write(self.index_path, "".join(json.dumps(item) + "\n" for item in records))
        return records

    @staticmethod
    def _record(run: AnalysisRun, path: Path) -> Dict[str, Any]:
        return {"run_id": run.run_id, "created_at": run.created_at, "query": run.query,
                "tickers": run.tickers, "path": str(path)}

    @staticmethod
    def _summary(run: AnalysisRun) -> str:
        lines = [f"# Analysis {run.run_id}", "", f"Query: {run.query}", "", "## Recommendations", ""]
        lines.extend(f"- {item.ticker}: {item.action} ({item.confidence}) — {item.reason}" for item in run.recommendations)
        if not run.recommendations:
            lines.append("No recommendations generated.")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
