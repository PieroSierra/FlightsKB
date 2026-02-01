"""Evaluation service for measuring retrieval quality."""

from pathlib import Path

import yaml

from src.models.query import EvalResult, TestQuery
from src.services.index import IndexService


class EvalService:
    """Service for evaluating retrieval quality."""

    def __init__(self, index_service: IndexService):
        """
        Initialize the eval service.

        Args:
            index_service: Index service for running queries.
        """
        self.index_service = index_service

    def load_test_queries(self, queries_path: Path) -> list[TestQuery]:
        """
        Load test queries from YAML file.

        Args:
            queries_path: Path to YAML file with test queries.

        Returns:
            List of TestQuery objects.
        """
        with open(queries_path) as f:
            data = yaml.safe_load(f)

        queries = []
        for item in data.get("queries", []):
            queries.append(TestQuery.from_dict(item))

        return queries

    def evaluate_query(self, test_query: TestQuery) -> EvalResult:
        """
        Evaluate a single test query.

        Args:
            test_query: Test query to evaluate.

        Returns:
            EvalResult with recall metrics.
        """
        # Run the query
        response = self.index_service.query(
            text=test_query.query,
            k=test_query.k,
        )

        # Get actual kb_ids from results
        actual_kb_ids = [r.kb_id for r in response.results]
        actual_chunk_ids = [r.chunk_id for r in response.results]

        # Calculate recall
        expected = set(test_query.expected_kb_ids)
        found = expected.intersection(set(actual_kb_ids))
        missed = expected - found

        # If using topics instead of kb_ids
        if test_query.expected_topics and not test_query.expected_kb_ids:
            # Check if any topic appears in results
            topics_found = 0
            for topic in test_query.expected_topics:
                topic_lower = topic.lower()
                for result in response.results:
                    if topic_lower in result.text.lower() or topic_lower in result.title.lower():
                        topics_found += 1
                        break
            recall = topics_found / len(test_query.expected_topics) if test_query.expected_topics else 0
        else:
            recall = len(found) / len(expected) if expected else 1.0

        return EvalResult(
            query_id=test_query.id,
            query_text=test_query.query,
            recall_at_k=recall,
            found=list(found),
            missed=list(missed),
            actual_results=actual_chunk_ids,
        )

    def run_evaluation(self, queries_path: Path) -> dict:
        """
        Run full evaluation against test queries.

        Args:
            queries_path: Path to test queries YAML.

        Returns:
            Dictionary with overall metrics and details.
        """
        test_queries = self.load_test_queries(queries_path)

        results = []
        for tq in test_queries:
            result = self.evaluate_query(tq)
            results.append(result)

        # Calculate overall metrics
        total = len(results)
        if total == 0:
            return {
                "total_queries": 0,
                "queries_passed": 0,
                "overall_recall": 0,
                "details": [],
            }

        queries_passed = sum(1 for r in results if r.recall_at_k >= 1.0)
        overall_recall = sum(r.recall_at_k for r in results) / total

        return {
            "total_queries": total,
            "queries_passed": queries_passed,
            "overall_recall": round(overall_recall, 2),
            "details": [r.to_dict() for r in results],
        }
