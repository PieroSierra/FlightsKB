# Research: Flights KB Playground

**Branch**: `001-flights-kb-playground`
**Created**: 2026-02-01

## Technology Decisions

### 1. Programming Language & Version

**Decision**: Python 3.11+

**Rationale**:
- Excellent ecosystem for NLP, embeddings, and vector databases
- ChromaDB, sentence-transformers, and all key dependencies have mature Python support
- Type hints and modern Python features improve code quality
- Widely understood by PMs who may need to modify templates

**Alternatives Considered**:
- TypeScript/Node.js: Good option but weaker NLP ecosystem
- Go: Faster but fewer embedding/vector libraries

---

### 2. Vector Database

**Decision**: ChromaDB (embedded mode with local persistence)

**Rationale**:
- Simplest API for prototyping - 5 lines to get started
- Built-in persistence with `persist_directory` parameter
- Full metadata filtering support via `where` clauses
- Zero external dependencies - runs in-process
- Install: `pip install chromadb`

**Alternatives Considered**:
| Database | Evaluated | Rejected Because |
|----------|-----------|------------------|
| LanceDB | Yes | Newer, smaller community, less documentation |
| Qdrant (local) | Yes | Heavier setup, overkill for playground |
| FAISS | Yes | No metadata filtering, no built-in persistence |
| Pinecone | No | Cloud-only, adds cost/complexity for prototype |

---

### 3. Embedding Model

**Decision**: sentence-transformers `all-MiniLM-L6-v2` (primary), with option to swap to OpenAI

**Rationale**:
- Free, local execution - no API costs during development
- Fast inference (~100ms per embedding)
- 384 dimensions - compact, efficient storage
- Good enough quality for semantic search on flight content
- Easy to swap to OpenAI `text-embedding-3-small` if quality needs increase

**Alternatives Considered**:
| Model | Evaluated | Notes |
|-------|-----------|-------|
| OpenAI text-embedding-3-small | Yes | Better quality, but adds API cost |
| OpenAI text-embedding-ada-002 | Yes | Legacy, being superseded |
| all-mpnet-base-v2 | Yes | Better quality but slower, 768 dims |

**Implementation Note**: Abstract embedding generation behind interface to allow swapping.

---

### 4. Testing Framework

**Decision**: pytest with pytest-cov

**Rationale**:
- Industry standard for Python testing
- Fixture-based testing works well with ChromaDB (use `tmp_path` for isolated test DBs)
- Rich plugin ecosystem
- Clear test discovery and reporting

**Test Structure**:
```
tests/
├── unit/           # Chunker, frontmatter parsing, ID generation
├── integration/    # Vector DB operations, end-to-end flows
└── contract/       # API endpoint contracts (if HTTP API implemented)
```

---

### 5. HTTP Framework (for optional API)

**Decision**: FastAPI

**Rationale**:
- Modern, async Python web framework
- Automatic OpenAPI documentation generation
- Built-in request validation with Pydantic
- Simple shared-secret auth via dependencies
- Lightweight enough for playground deployment

**Alternatives Considered**:
- Flask: Simpler but lacks async, no auto-docs
- Starlette: Too low-level for this use case

---

### 6. Hosting Platform

**Decision**: Railway or Render (cloud PaaS)

**Rationale**:
- Simple deployment from Git repository
- Persistent volume support for ChromaDB data
- Free tier sufficient for playground use
- No container/Kubernetes complexity

**Deployment Strategy**:
- Option A: Persist vector DB to volume, incremental updates
- Option B: Rebuild on deploy from knowledge/ (simpler, slower startup)

**Recommendation**: Start with Option B (rebuild on deploy) for simplicity.

---

### 7. CLI Framework

**Decision**: Click (Python CLI library)

**Rationale**:
- Clean decorator-based command definitions
- Built-in help generation
- Support for subcommands (query, ingest, rebuild, stats, eval)
- Easy to add JSON output mode

---

### 8. File Parsing (for ingestion)

**Decision**:
- Markdown: Built-in Python markdown parsing
- PDF: PyMuPDF (fitz) - lightweight, good text extraction
- HTML: BeautifulSoup4 - standard web scraping library
- YAML frontmatter: python-frontmatter library

---

## Dependency Summary

### Core Dependencies
```
chromadb>=0.4.0       # Vector database
sentence-transformers # Embedding model
click                 # CLI framework
python-frontmatter    # YAML frontmatter parsing
pyyaml                # YAML processing
```

### Optional Dependencies
```
fastapi               # HTTP API
uvicorn               # ASGI server
pymupdf               # PDF parsing
beautifulsoup4        # HTML parsing
httpx                 # URL fetching
```

### Development Dependencies
```
pytest                # Testing
pytest-cov            # Coverage
black                 # Formatting
ruff                  # Linting
```

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Which vector DB? | ChromaDB - simplest for prototyping |
| Which embedding model? | sentence-transformers MiniLM (free, local) |
| Cloud or local for prototype? | Cloud PaaS (Railway/Render) for PM access |
| Full API or CLI-only? | CLI primary, HTTP API optional but recommended |
| Incremental or full rebuild? | Full rebuild initially, incremental as nice-to-have |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Embedding quality insufficient | Interface abstraction allows OpenAI swap |
| ChromaDB scaling limits | Playground scope keeps data small; can migrate later |
| PDF parsing failures | Fallback to text-only mode, log warnings |
| Hosting costs | Free tiers sufficient; rebuild-on-deploy avoids persistence costs |
