"""Command-line interface for Flights KB."""

import json
import logging
import os
import sys
from pathlib import Path

import click

from src import __version__

# Default paths
DEFAULT_KNOWLEDGE_DIR = Path("knowledge")
DEFAULT_INDEX_DIR = Path("index")


def get_knowledge_dir() -> Path:
    """Get knowledge directory from env or default."""
    return Path(os.environ.get("FLIGHTSKB_KNOWLEDGE_DIR", DEFAULT_KNOWLEDGE_DIR))


def get_index_dir() -> Path:
    """Get index directory from env or default."""
    return Path(os.environ.get("FLIGHTSKB_INDEX_DIR", DEFAULT_INDEX_DIR))


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )


@click.group()
@click.version_option(version=__version__)
def cli():
    """Flights KB - A knowledge base for flight information."""
    pass


@cli.command()
@click.argument("text")
@click.option("--k", default=5, help="Number of results to return")
@click.option("--filters", default=None, help="Metadata filters (key=value,key=value)")
@click.option("--json-output", "json_out", is_flag=True, help="Output as JSON")
def query(text: str, k: int, filters: str, json_out: bool):
    """Search the knowledge base."""
    from src.services.index import IndexService

    index_service = IndexService(
        index_dir=get_index_dir(),
        knowledge_dir=get_knowledge_dir(),
    )

    # Parse filters
    filter_dict = None
    if filters:
        filter_dict = {}
        for part in filters.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                filter_dict[key.strip()] = value.strip()

    # Execute query
    response = index_service.query(text=text, k=k, filters=filter_dict)

    if json_out:
        click.echo(json.dumps(response.to_dict(), indent=2))
    else:
        _print_query_results(response)


def _print_query_results(response):
    """Print query results in human-readable format."""
    click.echo(f'Query: "{response.query}"')
    click.echo(f"Results: {response.total_results}")
    click.echo()

    if not response.results:
        click.echo("No results found. Try a different query or rebuild the index.")
        return

    for i, result in enumerate(response.results, 1):
        click.echo(f"[{i}] Score: {result.score:.2f}")
        click.echo(f"    Title: {result.title}")
        click.echo(f"    File: {result.file_path or 'unknown'}")
        click.echo(f"    ID: {result.chunk_id}")
        click.echo("    ---")

        # Show excerpt (first 200 chars)
        excerpt = result.text[:200].replace("\n", " ")
        if len(result.text) > 200:
            excerpt += "..."
        click.echo(f"    {excerpt}")
        click.echo()


@cli.command()
@click.option("--verbose", is_flag=True, help="Show detailed progress")
def rebuild(verbose: bool):
    """Rebuild the vector index from knowledge files."""
    from src.services.index import IndexService

    setup_logging(verbose)

    click.echo("Rebuilding index...")

    index_service = IndexService(
        index_dir=get_index_dir(),
        knowledge_dir=get_knowledge_dir(),
    )

    result = index_service.rebuild(verbose=verbose)

    click.echo()
    click.echo("Rebuild complete:")
    click.echo(f"  Documents: {result['documents_processed']}")
    click.echo(f"  Chunks: {result['chunks_indexed']}")
    click.echo(f"  Duration: {result['duration_seconds']:.1f}s")

    if result["errors"]:
        click.echo()
        click.echo(f"Warnings ({len(result['errors'])}):")
        for error in result["errors"]:
            click.echo(f"  - {error}")


@cli.command()
@click.option("--text", default=None, help="Raw text to ingest")
@click.option("--file", "file_path", default=None, type=click.Path(exists=True), help="File to ingest")
@click.option("--source-kind", default="internal", help="Source kind (internal, ugc, blog, etc.)")
@click.option("--source-name", default="manual", help="Source name/author")
def ingest(text: str, file_path: str, source_kind: str, source_name: str):
    """Ingest new knowledge into the system."""
    from src.services.ingest import IngestService

    if not text and not file_path:
        click.echo("Error: Provide either --text or --file", err=True)
        sys.exit(1)

    ingest_service = IngestService(knowledge_dir=get_knowledge_dir())

    if text:
        result = ingest_service.ingest_text(
            text=text,
            source_kind=source_kind,
            source_name=source_name,
        )
    else:
        result = ingest_service.ingest_file(
            file_path=Path(file_path),
            source_kind=source_kind,
            source_name=source_name,
        )

    click.echo(f"Ingested: {result['output_file']}")
    click.echo(f"  kb_id: {result['kb_id']}")
    click.echo(f"  cards: {result['card_count']}")
    click.echo()
    click.echo("Run 'flightskb rebuild' to index the new content.")


@cli.command()
@click.option("--detailed", is_flag=True, help="Show detailed breakdowns")
@click.option("--json-output", "json_out", is_flag=True, help="Output as JSON")
def stats(detailed: bool, json_out: bool):
    """Show knowledge base statistics."""
    from src.services.index import IndexService

    index_service = IndexService(
        index_dir=get_index_dir(),
        knowledge_dir=get_knowledge_dir(),
    )

    stats_data = index_service.get_stats()

    if json_out:
        click.echo(json.dumps(stats_data, indent=2))
    else:
        _print_stats(stats_data, detailed)


def _print_stats(stats_data: dict, detailed: bool):
    """Print stats in human-readable format."""
    click.echo("Flights KB Statistics")
    click.echo("=" * 21)
    click.echo()
    click.echo(f"Documents: {stats_data['document_count']}")
    click.echo(f"Chunks: {stats_data['chunk_count']}")

    if detailed and stats_data.get("by_type"):
        click.echo()
        click.echo("By Type:")
        for doc_type, count in sorted(stats_data["by_type"].items()):
            click.echo(f"  {doc_type}: {count}")

    if detailed and stats_data.get("by_category"):
        click.echo()
        click.echo("By Category:")
        for category, count in sorted(stats_data["by_category"].items()):
            click.echo(f"  {category}: {count}")

    if detailed and stats_data.get("by_confidence"):
        click.echo()
        click.echo("By Confidence:")
        for conf, count in sorted(stats_data["by_confidence"].items()):
            click.echo(f"  {conf}: {count}")

    if detailed and stats_data.get("by_status"):
        click.echo()
        click.echo("By Status:")
        for status, count in sorted(stats_data["by_status"].items()):
            click.echo(f"  {status}: {count}")

    click.echo()
    click.echo("Index Info:")
    idx_meta = stats_data.get("index_metadata", {})
    click.echo(f"  Last rebuild: {idx_meta.get('last_rebuild', 'never')}")
    click.echo(f"  Model: {idx_meta.get('embedding_model', 'unknown')}")
    click.echo(f"  Vector DB: {idx_meta.get('vector_db_type', 'unknown')}")


@cli.command("eval")
@click.option("--queries", default="eval/test_queries.yaml", help="Path to test queries YAML")
@click.option("--verbose", is_flag=True, help="Show detailed results")
def run_eval(queries: str, verbose: bool):
    """Evaluate retrieval quality against test queries."""
    from src.services.eval import EvalService
    from src.services.index import IndexService

    queries_path = Path(queries)
    if not queries_path.exists():
        click.echo(f"Error: Test queries file not found: {queries}", err=True)
        sys.exit(1)

    index_service = IndexService(
        index_dir=get_index_dir(),
        knowledge_dir=get_knowledge_dir(),
    )

    eval_service = EvalService(index_service=index_service)
    results = eval_service.run_evaluation(queries_path)

    _print_eval_results(results, verbose)


def _print_eval_results(results: dict, verbose: bool):
    """Print evaluation results."""
    click.echo(f"Running evaluation: {results['total_queries']} test queries")
    click.echo()
    click.echo("Results:")
    click.echo(f"  Recall@k: {results['overall_recall']:.2f} ({results['queries_passed']}/{results['total_queries']} queries found expected results)")

    if verbose and results.get("details"):
        click.echo()
        click.echo("Details:")
        for detail in results["details"]:
            status = "PASS" if detail["recall_at_k"] >= 1.0 else "MISS"
            click.echo(f"  [{status}] {detail['query_id']}: {detail['query_text'][:50]}")
            if detail["missed"]:
                click.echo(f"       Expected: {', '.join(detail['missed'])}")
                click.echo(f"       Got: {', '.join(detail['actual_results'][:3])}")

    click.echo()
    threshold = 0.90
    status = "PASS" if results["overall_recall"] >= threshold else "FAIL"
    click.echo(f"Overall: {status} (>= {threshold} threshold)")


@cli.command()
@click.option("--port", default=8000, help="Port to listen on")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
def serve(port: int, host: str):
    """Start the HTTP API server."""
    try:
        import uvicorn
        from src.api.app import create_app
    except ImportError:
        click.echo("Error: API dependencies not installed. Run: pip install flightskb[api]", err=True)
        sys.exit(1)

    app = create_app(
        index_dir=get_index_dir(),
        knowledge_dir=get_knowledge_dir(),
    )

    click.echo(f"Starting Flights KB API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
