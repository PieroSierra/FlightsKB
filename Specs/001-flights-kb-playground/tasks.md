# Tasks: Flights KB Playground

**Input**: Design documents from `/specs/001-flights-kb-playground/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks excluded per spec.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Paths follow single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and package configuration

- [x] T001 Create project structure with src/, tests/, knowledge/, templates/, eval/, index/ directories
- [x] T002 Initialize Python project with pyproject.toml (Python 3.11+, ChromaDB, sentence-transformers, Click, python-frontmatter)
- [x] T003 [P] Create .gitignore (exclude index/chroma_db/, .env, __pycache__, .venv/)
- [x] T004 [P] Create .env.example with FLIGHTSKB_API_KEY placeholder
- [x] T005 [P] Create knowledge/ subdirectories (airlines/, airports/, loyalty/, hacks/, lounges/, reviews/, pricing-curves/, inbox/)
- [x] T006 [P] Create README.md with project overview and quickstart reference

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, services, and CLI framework that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Models

- [x] T007 [P] Create Document model with frontmatter parsing in src/models/document.py
- [x] T008 [P] Create Chunk model with card-level fields in src/models/chunk.py
- [x] T009 [P] Create QueryResult model in src/models/query.py
- [x] T010 Create Source model (nested in Document) in src/models/document.py

### Core Services

- [x] T011 Implement deterministic Chunker service in src/services/chunker.py (chunk_id = kb_id#slug(heading), content hash)
- [x] T012 Implement EmbeddingService wrapper for sentence-transformers in src/services/embeddings.py
- [x] T013 Implement IndexService for ChromaDB operations (add, query, rebuild, get_stats) in src/services/index.py

### CLI Framework

- [x] T014 Create CLI entry point with Click in src/cli.py (skeleton with subcommands: query, rebuild, ingest, stats, eval)
- [x] T015 [P] Create src/__init__.py with version info
- [x] T016 [P] Create src/models/__init__.py exporting Document, Chunk, QueryResult
- [x] T017 [P] Create src/services/__init__.py exporting Chunker, EmbeddingService, IndexService

### Templates

- [x] T018 [P] Create airline_premium_fare_template.md in templates/
- [x] T019 [P] Create hack_template.md in templates/

**Checkpoint**: Foundation ready - CLI skeleton exists, models parse frontmatter, ChromaDB integration works

---

## Phase 3: User Story 1 - Query Knowledge Base (Priority: P1) 🎯 MVP

**Goal**: Enable semantic search with natural language queries and metadata filtering

**Independent Test**: Run `flightskb query "business class tips"` and verify ranked results with scores, titles, metadata, and file paths are returned

### Implementation for User Story 1

- [x] T020 [US1] Implement query logic in IndexService.query() with text, k, and filters support in src/services/index.py
- [x] T021 [US1] Implement `query` CLI command in src/cli.py (--text, --k, --filters, --json output)
- [x] T022 [US1] Add result formatting with scores, titles, excerpts, metadata, chunk_id, and file_path in src/cli.py
- [x] T023 [US1] Handle empty result set with helpful message in src/cli.py
- [x] T024 [US1] Add filter parsing for airline, route, cabin, type, confidence, status in src/services/index.py

**Checkpoint**: User Story 1 complete - `flightskb query` works end-to-end with filters

---

## Phase 4: User Story 2 - Rebuild Vector Index (Priority: P1)

**Goal**: Regenerate vector index from all Markdown files in knowledge/ directory

**Independent Test**: Add/modify a knowledge file, run `flightskb rebuild`, then query and verify updated content appears

### Implementation for User Story 2

- [x] T025 [US2] Implement rebuild logic: scan knowledge/, parse docs, chunk, embed, upsert to ChromaDB in src/services/index.py
- [x] T026 [US2] Implement `rebuild` CLI command in src/cli.py (--verbose flag)
- [x] T027 [US2] Add progress reporting (documents processed, chunks indexed, duration) in src/cli.py
- [x] T028 [US2] Handle malformed frontmatter gracefully (skip file, log warning, continue) in src/services/chunker.py
- [x] T029 [US2] Handle empty knowledge directory (report zero documents, complete without error) in src/services/index.py
- [x] T030 [US2] Store rebuild metadata (last_rebuild timestamp, embedding_model, chunk_count) in index/ in src/services/index.py

**Checkpoint**: User Story 2 complete - `flightskb rebuild` processes all knowledge and creates searchable index

---

## Phase 5: User Story 3 - Ingest New Knowledge (Priority: P2)

**Goal**: Add new knowledge via text input or file upload, generating proper frontmatter and cards

**Independent Test**: Run `flightskb ingest --file article.pdf`, verify Markdown file appears in knowledge/inbox/ with frontmatter

### Implementation for User Story 3

- [x] T031 [P] [US3] Implement text ingestion (stdin/argument) in src/services/ingest.py
- [x] T032 [P] [US3] Implement Markdown file ingestion (.md) in src/services/ingest.py
- [x] T033 [P] [US3] Implement plain text file ingestion (.txt) in src/services/ingest.py
- [x] T034 [US3] Implement PDF ingestion with PyMuPDF in src/services/ingest.py
- [x] T035 [US3] Implement HTML ingestion with BeautifulSoup4 in src/services/ingest.py
- [x] T036 [US3] Generate kb_id (UUID-based), auto-populate frontmatter (type, title, dates, status=draft, source, confidence=medium) in src/services/ingest.py
- [x] T037 [US3] Implement heuristic chunking (split into ## sections) in src/services/ingest.py
- [x] T038 [US3] Implement `ingest` CLI command in src/cli.py (--text, --file, --source-kind, --source-name)
- [x] T039 [US3] Save output to knowledge/inbox/{generated-filename}.md in src/services/ingest.py

**Checkpoint**: User Story 3 complete - `flightskb ingest` accepts text/files and creates properly formatted Markdown

---

## Phase 6: User Story 4 - View KB Statistics (Priority: P2)

**Goal**: Display knowledge base composition metrics and index metadata

**Independent Test**: Run `flightskb stats`, verify document count, chunk count, breakdowns, and index info displayed

### Implementation for User Story 4

- [x] T040 [US4] Implement stats aggregation in IndexService.get_stats() in src/services/index.py
- [x] T041 [US4] Add grouping by type, category (folder), confidence, status in src/services/index.py
- [x] T042 [US4] Implement `stats` CLI command in src/cli.py (--detailed, --json flags)
- [x] T043 [US4] Format stats output (totals, breakdowns, index metadata: last_rebuild, model, db_type) in src/cli.py

**Checkpoint**: User Story 4 complete - `flightskb stats` shows full KB visibility

---

## Phase 7: User Story 5 - Evaluate Retrieval Quality (Priority: P3)

**Goal**: Run evaluation against test queries and report recall@k metrics

**Independent Test**: Run `flightskb eval`, verify recall metrics and miss highlighting for test queries

### Implementation for User Story 5

- [x] T044 [P] [US5] Create TestQuery model in src/models/query.py
- [x] T045 [P] [US5] Create sample test_queries.yaml with ~5 starter queries in eval/
- [x] T046 [US5] Implement EvalService to load YAML, run queries, compute recall@k in src/services/eval.py
- [x] T047 [US5] Implement `eval` CLI command in src/cli.py (--queries file path, --verbose)
- [x] T048 [US5] Format eval output (recall@k, found/missed per query, pass/fail summary) in src/cli.py

**Checkpoint**: User Story 5 complete - `flightskb eval` validates retrieval quality

---

## Phase 8: Optional HTTP API (Priority: P3)

**Goal**: Expose query, stats, rebuild via HTTP for remote PM access

**Independent Test**: Start server, POST to /query, verify JSON response matches CLI output

### Implementation for HTTP API

- [x] T049 [P] Create FastAPI app skeleton in src/api/app.py
- [x] T050 [P] Implement /health endpoint in src/api/routes.py
- [x] T051 [US1] Implement POST /query endpoint (maps to IndexService.query) in src/api/routes.py
- [x] T052 [US4] Implement GET /stats endpoint (maps to IndexService.get_stats) in src/api/routes.py
- [x] T053 [US2] Implement POST /rebuild endpoint with X-API-Key auth in src/api/routes.py
- [x] T054 Add `serve` CLI command to start uvicorn in src/cli.py (--port, --host)
- [x] T055 [P] Create src/api/__init__.py

**Checkpoint**: HTTP API complete - remote access available for PMs

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Sample content, documentation, and deployment prep

- [x] T056 [P] Create 2-3 sample knowledge documents in knowledge/hacks/ and knowledge/airlines/
- [x] T057 [P] Update README.md with full CLI usage and examples
- [x] T058 Validate quickstart.md scenarios work end-to-end
- [x] T059 [P] Create Procfile or railway.json for Render/Railway deployment
- [x] T060 Final code cleanup and docstrings for public interfaces

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1 Query (Phase 3)**: Depends on Foundational
- **US2 Rebuild (Phase 4)**: Depends on Foundational
- **US3 Ingest (Phase 5)**: Depends on Foundational
- **US4 Stats (Phase 6)**: Depends on Foundational + US2 (needs rebuild metadata)
- **US5 Eval (Phase 7)**: Depends on US1 (needs query working)
- **HTTP API (Phase 8)**: Depends on US1, US2, US4
- **Polish (Phase 9)**: Depends on desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    │
    ├──► US1 Query (P1) ──────────────────────────┐
    │                                              │
    ├──► US2 Rebuild (P1) ──► US4 Stats (P2)      ├──► US5 Eval (P3)
    │                                              │
    └──► US3 Ingest (P2)                          │
                                                   │
                                          HTTP API (P3) ◄─┘
```

### Parallel Opportunities

**Phase 1 - All parallel**:
- T003, T004, T005, T006 can run simultaneously

**Phase 2 - Model parallelism**:
- T007, T008, T009 (models) can run in parallel
- T018, T019 (templates) can run in parallel

**Phase 3-4 - Story parallelism**:
- US1 (Query) and US2 (Rebuild) can run in parallel after Foundational

**Phase 5 - Ingest file types**:
- T031, T032, T033 (text, md, txt ingestion) can run in parallel

---

## Parallel Example: Foundational Models

```bash
# Launch all models together:
Task: "Create Document model in src/models/document.py"
Task: "Create Chunk model in src/models/chunk.py"
Task: "Create QueryResult model in src/models/query.py"
```

## Parallel Example: User Stories 1 & 2

```bash
# After Foundational complete, launch both P1 stories:
Task: "US1 - Implement query logic in IndexService"
Task: "US2 - Implement rebuild logic in IndexService"
```

---

## Implementation Strategy

### MVP First (Query + Rebuild)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 Query
4. Complete Phase 4: US2 Rebuild
5. **STOP and VALIDATE**: Seed sample content, rebuild, query - demo to PM team
6. Continue with US3-US5 as time permits

### Hackathon Timeline Suggestion

| Block | Phases | Deliverable |
|-------|--------|-------------|
| Hour 1 | Setup + Foundational (T001-T019) | Project skeleton, models, CLI framework |
| Hour 2 | US1 Query + US2 Rebuild (T020-T030) | Core search + index rebuild working |
| Hour 3 | US3 Ingest (T031-T039) | Add knowledge via CLI |
| Hour 4 | US4 Stats + Polish (T040-T043, T056-T060) | Stats + sample content + demo prep |

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 Query → Test `query` command → Demo
3. Add US2 Rebuild → Test `rebuild` command → Demo (Full MVP!)
4. Add US3 Ingest → Test `ingest` command → Demo
5. Add US4 Stats → Test `stats` command → Demo
6. Add US5 Eval → Test `eval` command → Final demo

---

## Notes

- [P] tasks = different files, no dependencies - safe to parallelize
- [Story] label maps task to specific user story for traceability
- US1 (Query) and US2 (Rebuild) are both P1 - complete both for functional MVP
- HTTP API is optional - prioritize CLI for hackathon
- Commit after each task or logical group
- Stop at any checkpoint to validate and demo
