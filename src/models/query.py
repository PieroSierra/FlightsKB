"""Query and result models for knowledge base search."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryResult:
    """A single search result from the knowledge base."""

    chunk_id: str
    kb_id: str
    title: str
    text: str
    score: float
    metadata: dict = field(default_factory=dict)
    file_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "chunk_id": self.chunk_id,
            "kb_id": self.kb_id,
            "title": self.title,
            "text": self.text,
            "score": self.score,
            "metadata": self.metadata,
            "file_path": self.file_path,
        }


@dataclass
class QueryResponse:
    """Response from a knowledge base query."""

    query: str
    total_results: int
    results: list[QueryResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "total_results": self.total_results,
            "results": [r.to_dict() for r in self.results],
        }


@dataclass
class TestQuery:
    """An evaluation test query with expected results."""

    id: str
    query: str
    expected_kb_ids: list[str] = field(default_factory=list)
    expected_topics: list[str] = field(default_factory=list)
    k: int = 3

    @classmethod
    def from_dict(cls, data: dict) -> "TestQuery":
        """Parse from YAML dictionary."""
        return cls(
            id=data["id"],
            query=data["query"],
            expected_kb_ids=data.get("expected_kb_ids", []),
            expected_topics=data.get("expected_topics", []),
            k=data.get("k", 3),
        )


@dataclass
class EvalResult:
    """Result of evaluating a single test query."""

    query_id: str
    query_text: str
    recall_at_k: float
    found: list[str] = field(default_factory=list)
    missed: list[str] = field(default_factory=list)
    actual_results: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "recall_at_k": self.recall_at_k,
            "found": self.found,
            "missed": self.missed,
            "actual_results": self.actual_results,
        }
