# Flights KB Playground

A lightweight knowledge base for flight-related information with semantic search capabilities.

**Status**: Hackathon prototype - not for production use.

## Features

- Store flight knowledge as human-editable Markdown files
- Semantic search using vector embeddings
- CLI for query, ingest, rebuild, and stats
- Optional HTTP API for remote access

## Quick Start

```bash
# Install
pip install -e ".[all]"

# Initialize and rebuild index
flightskb rebuild

# Query the knowledge base
flightskb query "business class tips for LHR to JFK"

# View statistics
flightskb stats
```

## Documentation

See [specs/001-flights-kb-playground/quickstart.md](specs/001-flights-kb-playground/quickstart.md) for detailed usage.

## Project Structure

```
knowledge/          # Markdown knowledge files (source of truth)
templates/          # Document templates for PMs
src/                # Python source code
eval/               # Evaluation test queries
index/              # Generated vector index (gitignored)
```

## License

MIT - Playground/prototype only.
