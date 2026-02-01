# Implementation Plan: Flights KB Playground

**Branch**: `001-flights-kb-playground` | **Date**: 2026-02-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-flights-kb-playground/spec.md`

## Summary

Build a lightweight knowledge base system that stores flight-related knowledge as human-editable Markdown files, generates a derived vector index using ChromaDB for semantic retrieval, and exposes a CLI console (with optional HTTP API) for ingestion, inspection, querying, rebuilds, and stats. Designed for internal PM prototype access, not production-grade.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: ChromaDB, sentence-transformers, Click, python-frontmatter, FastAPI (optional)
**Storage**: File system (Markdown in `knowledge/`) + ChromaDB (vector index)
**Testing**: pytest with pytest-cov
**Target Platform**: Cloud PaaS (Railway/Render) for API; CLI runs locally
**Project Type**: Single project with CLI + optional HTTP API
**Performance Goals**: Query response <2 seconds, rebuild completes for ~100 documents
**Constraints**: Playground-grade (no production security, scale, or uptime requirements)
**Scale/Scope**: ~100 documents, ~500 chunks, single PM team users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Project constitution is template-only (no specific principles defined yet).

Default gates applied:
- [x] **Simplicity**: Single project structure, minimal dependencies
- [x] **Testability**: pytest-based testing with unit/integration split
- [x] **No over-engineering**: File-based storage, embedded vector DB, no external services

## Project Structure

### Documentation (this feature)

```text
specs/001-flights-kb-playground/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions (complete)
├── data-model.md        # Entity definitions (complete)
├── quickstart.md        # Usage guide (complete)
├── contracts/           # API specifications (complete)
│   └── openapi.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (next: /speckit.tasks)
```

### Source Code (repository root)

```text
flights-kb/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Click CLI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py     # Document/frontmatter parsing
│   │   ├── chunk.py        # Chunk/card extraction
│   │   └── query.py        # Query/result models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunker.py      # Deterministic chunking
│   │   ├── embeddings.py   # Embedding generation
│   │   ├── index.py        # ChromaDB operations
│   │   ├── ingest.py       # Content ingestion
│   │   └── eval.py         # Evaluation runner
│   └── api/                # Optional HTTP API
│       ├── __init__.py
│       ├── app.py          # FastAPI application
│       └── routes.py       # Endpoint handlers
├── tests/
│   ├── conftest.py         # Shared fixtures
│   ├── unit/
│   │   ├── test_chunker.py
│   │   ├── test_document.py
│   │   └── test_frontmatter.py
│   ├── integration/
│   │   ├── test_index.py
│   │   └── test_ingest.py
│   └── contract/
│       └── test_api.py
├── knowledge/              # Knowledge content (source of truth)
│   ├── airlines/
│   ├── airports/
│   ├── loyalty/
│   ├── hacks/
│   ├── lounges/
│   ├── reviews/
│   ├── pricing-curves/
│   └── inbox/
├── templates/              # Document templates
│   ├── airline_premium_fare_template.md
│   └── hack_template.md
├── eval/                   # Evaluation data
│   └── test_queries.yaml
├── index/                  # Generated index data
│   ├── manifests/
│   └── chroma_db/
├── pyproject.toml          # Package configuration
├── README.md               # Project documentation
└── .env.example            # Environment variable template
```

**Structure Decision**: Single project with `src/` layout. Models, services, and optional API are co-located. Knowledge content lives at repository root for easy PM access. Index directory is gitignored (derived from source).

## Complexity Tracking

> No constitution violations requiring justification.

| Decision | Rationale |
|----------|-----------|
| Single Python package | Simplest structure for playground scope |
| ChromaDB embedded | No external database to manage |
| Optional HTTP API | Core value via CLI; API adds PM accessibility |
| File-based knowledge storage | Human-editable, version-controlled, no DB dependency |

## Phase Completion Status

- [x] **Phase 0**: Research complete - see [research.md](./research.md)
- [x] **Phase 1**: Design complete
  - [data-model.md](./data-model.md) - Entity definitions
  - [contracts/openapi.yaml](./contracts/openapi.yaml) - API specification
  - [quickstart.md](./quickstart.md) - Usage guide
- [x] **Phase 2**: Tasks complete - see [tasks.md](./tasks.md)

## Next Steps

Run `/speckit.implement` to begin task execution, or use `/speckit.taskstoissues` to create GitHub issues.
