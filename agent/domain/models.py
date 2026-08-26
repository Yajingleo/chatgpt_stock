"""Typed stock-analysis domain models and stable serialization."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


class RecommendationAction(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


@dataclass(frozen=True)
class NewsArticle:
    ticker: str
    title: str
    url: str = ""
    published: str = ""
    summary: str = ""
    excerpt: str = ""

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "NewsArticle":
        content = value.get("content", "") or ""
        return cls(
            str(value.get("ticker", "")).upper(),
            str(value.get("title", "")),
            str(value.get("url", "")),
            str(value.get("published", "")),
            str(value.get("summary", "")),
            content[:1000],
        )


@dataclass(frozen=True)
class SentimentAnalysis:
    ticker: str
    score: float
    confidence: str = "low"
    news_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    key_phrases: List[str] = field(default_factory=list)

    @classmethod
    def from_pair(cls, ticker: str, value: Dict[str, Any]) -> "SentimentAnalysis":
        return cls(
            ticker.upper(),
            float(value.get("sentiment_score", 0)),
            str(value.get("confidence", "low")),
            int(value.get("news_count", 0)),
            int(value.get("positive_count", 0)),
            int(value.get("negative_count", 0)),
            list(value.get("key_phrases", []))[:10],
        )


@dataclass(frozen=True)
class Recommendation:
    ticker: str
    action: str
    confidence: str
    sentiment_score: float
    reason: str = ""

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Recommendation":
        return cls(
            str(value.get("ticker", "")).upper(),
            str(value.get("action", RecommendationAction.HOLD.value)),
            str(value.get("confidence", "low")),
            float(value.get("sentiment_score", 0)),
            str(value.get("reason", "")),
        )


@dataclass
class AnalysisRun:
    run_id: str
    query: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    tickers: List[str] = field(default_factory=list)
    articles: List[NewsArticle] = field(default_factory=list)
    sentiment: List[SentimentAnalysis] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "AnalysisRun":
        return cls(
            value["run_id"],
            value.get("query", ""),
            value.get("created_at", ""),
            list(value.get("tickers", [])),
            [NewsArticle(**item) for item in value.get("articles", [])],
            [SentimentAnalysis(**item) for item in value.get("sentiment", [])],
            [Recommendation(**item) for item in value.get("recommendations", [])],
            dict(value.get("provenance", {})),
            int(value.get("schema_version", 1)),
        )


AgentResponse = Dict[str, Any]
ToolResult = Dict[str, Any]
