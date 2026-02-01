# Feature Specification: Flights KB Playground

**Feature Branch**: `001-flights-kb-playground`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "Build Flights KB Playground - a lightweight knowledge base system for storing flight-related knowledge"

## Clarifications

### Session 2026-02-01

- Q: Should URL ingestion be included in initial build or deferred? → A: Deferred; support text/file only for hackathon scope

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Knowledge Base (Priority: P1)

A Product Manager wants to find relevant flight information by asking natural language questions. They type a query like "business class tips for LHR to JFK" and receive ranked results showing relevant knowledge cards with scores, titles, excerpts, and source links.

**Why this priority**: This is the core value proposition - enabling semantic search across flight knowledge. Without querying, the system provides no user value.

**Independent Test**: Can be fully tested by entering a query and verifying relevant results are returned with scores and metadata.

**Acceptance Scenarios**:

1. **Given** the knowledge base contains indexed cards, **When** a user submits a text query with optional filters, **Then** the system returns the top-k most relevant results with chunk titles, text excerpts, metadata, and similarity scores
2. **Given** a query is submitted, **When** results are returned, **Then** each result includes a back-link to the source file path and chunk ID
3. **Given** a query includes metadata filters (airline, route, cabin), **When** the query is executed, **Then** only chunks matching the filter criteria are returned

---

### User Story 2 - Rebuild Vector Index (Priority: P1)

A PM or administrator needs to regenerate the vector index after knowledge files have been added or modified. They run a rebuild command and the system processes all Markdown files in the knowledge folder, generating fresh embeddings and updating the index.

**Why this priority**: Without rebuilding, new or changed content cannot be searched. This is essential for keeping the index in sync with source content.

**Independent Test**: Can be tested by modifying a knowledge file, running rebuild, and verifying the changes appear in query results.

**Acceptance Scenarios**:

1. **Given** Markdown files exist in the knowledge directory, **When** a rebuild is triggered, **Then** the system parses all files, extracts chunks, generates embeddings, and updates the vector index
2. **Given** a rebuild completes, **When** querying the index, **Then** all current knowledge content is searchable
3. **Given** a rebuild is running, **When** it completes, **Then** the system reports the number of documents processed, chunks indexed, and time taken

---

### User Story 3 - Ingest New Knowledge (Priority: P2)

A PM wants to add new flight-related knowledge to the system. They can paste raw text or upload a local file (.txt, .md, .pdf, .html). The system processes the content, extracts knowledge cards, generates proper frontmatter with provenance metadata, and saves structured Markdown files to the inbox folder.

**Why this priority**: Adding knowledge is essential for growing the KB, but initial value can be delivered with pre-seeded content. This enables ongoing KB expansion.

**Independent Test**: Can be tested by ingesting content from any supported source and verifying properly formatted Markdown files appear in the inbox folder.

**Acceptance Scenarios**:

1. **Given** raw text is provided, **When** ingestion is triggered, **Then** the system creates a Markdown file with YAML frontmatter (kb_id, type, title, dates, status, source, confidence) and content split into ## card sections
2. **Given** a file is uploaded, **When** ingestion completes, **Then** the file is processed, chunked heuristically, and saved to `knowledge/inbox/` with proper provenance metadata
3. *(Deferred)* URL ingestion excluded from initial hackathon build

---

### User Story 4 - View Knowledge Base Statistics (Priority: P2)

A PM wants to understand the current state of the knowledge base. They request stats and see total documents, total chunks, breakdowns by type/category/confidence/status, last rebuild time, embedding model name, and vector DB type.

**Why this priority**: Statistics provide visibility into KB health and coverage, supporting informed curation decisions.

**Independent Test**: Can be tested by running the stats command and verifying all expected metrics are displayed.

**Acceptance Scenarios**:

1. **Given** the knowledge base has indexed content, **When** stats are requested, **Then** the system displays total document count and total chunk count
2. **Given** stats are requested, **When** displayed, **Then** the output includes chunks grouped by type, category, confidence level, and status
3. **Given** a rebuild has occurred, **When** stats are requested, **Then** the last rebuild timestamp, embedding model name, and vector DB type are shown

---

### User Story 5 - Evaluate Retrieval Quality (Priority: P3)

An administrator wants to verify the knowledge base retrieval quality hasn't degraded. They run an evaluation against a predefined set of test queries with expected results and see a recall@k report highlighting any misses.

**Why this priority**: Evaluation prevents silent quality degradation as the KB grows, but initial deployment can proceed without it.

**Independent Test**: Can be tested by running eval against the test queries YAML file and verifying recall metrics and miss reports are generated.

**Acceptance Scenarios**:

1. **Given** a YAML file with ~20 test queries and expected target kb_ids exists, **When** evaluation is run, **Then** the system reports recall@k metrics for each query
2. **Given** evaluation completes, **When** results are displayed, **Then** any queries that failed to return expected results are highlighted with the actual vs expected chunks

---

### Edge Cases

- What happens when no Markdown files exist in the knowledge directory? System should report zero documents and allow rebuild to complete without error
- What happens when a query matches no results? System should return an empty result set with a helpful message
- What happens when ingested content lacks clear section boundaries? System should apply heuristic chunking and flag for manual review
- What happens when the same content is ingested twice? System should generate a new kb_id (deduplication is optional)
- What happens when a Markdown file has malformed YAML frontmatter? System should skip the file, log a warning, and continue processing other files
- What happens when the vector DB is unavailable? System should report an error and fail gracefully without data loss

## Requirements *(mandatory)*

### Functional Requirements

**Knowledge Storage**
- **FR-001**: System MUST store knowledge as human-editable Markdown files in a `knowledge/` folder structure
- **FR-002**: System MUST organize knowledge into category-based subfolders (airlines, loyalty, hacks, airports, lounges, reviews, pricing-curves, inbox)
- **FR-003**: Each Markdown file MUST have YAML frontmatter with required fields: kb_id, type, title, created, updated, status, source (kind, name, url, retrieved), and confidence
- **FR-004**: System MUST support optional YAML fields: tags, entities (airline, alliance, airports, routes, cabins, aircraft, flight_numbers), temporal (effective_from, effective_to), geo, audience, license

**Chunking**
- **FR-005**: System MUST treat each `## <heading>` section as one chunk ("card")
- **FR-006**: System MUST generate deterministic chunk IDs using format `${kb_id}#${slug(heading)}`
- **FR-007**: Each chunk record MUST include: chunk_id, doc_id, title, text, metadata (merged doc + card level), source, and content hash
- **FR-008**: Running the chunker twice on identical content MUST produce identical chunk_ids and text

**Vector Index**
- **FR-009**: System MUST generate embeddings for each chunk and store in a vector database
- **FR-010**: System MUST support vector index rebuild from Markdown source at any time
- **FR-011**: System MUST support filtered queries by metadata attributes (airline, route, cabin, etc.)
- **FR-012**: Query results MUST include chunk_id, kb_id, title, text, metadata, and similarity score

**Console Interface**
- **FR-013**: System MUST provide a command-line interface for query, ingest, rebuild, and stats operations
- **FR-014**: Query command MUST accept parameters: text query, k (number of results), and optional filters
- **FR-015**: Ingest command MUST accept: raw text and local files (.txt, .md, .pdf, .html)
- **FR-016**: System MUST save ingested content to `knowledge/inbox/` with proper frontmatter and provenance

**Provenance & Licensing**
- **FR-017**: Every ingested document MUST record source kind, name, URL (if applicable), and retrieved date
- **FR-018**: System MUST track license.reuse flag (ok, restricted, unknown) for each document
- **FR-019**: System MUST default license.reuse to "unknown" for web content unless explicitly marked safe

**Evaluation**
- **FR-020**: System MUST support loading test queries from a YAML file with expected target kb_ids
- **FR-021**: Evaluation command MUST report recall@k metrics and highlight misses

**API (Optional)**
- **FR-022**: System MAY expose an HTTP API with endpoints: /query, /stats, /rebuild
- **FR-023**: Write operations (ingest, rebuild) MUST be protected by a shared secret token

### Key Entities

- **Document**: A Markdown file representing a unit of knowledge with frontmatter metadata (kb_id, type, title, dates, status, source, confidence) and content organized into cards
- **Card/Chunk**: A section within a document (marked by `## heading`) representing a single searchable unit with claim type, applies-to selector, summary, and optional details
- **Vector Index**: Derived data structure containing embeddings for all chunks, rebuildable from source Markdown
- **Source**: Provenance information tracking where knowledge originated (internal, UGC, marketing, press, blog, forum, other) with URL and retrieval date
- **Test Query**: An evaluation record pairing a query string with expected kb_ids to measure retrieval quality

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find relevant knowledge by natural language query and receive ranked results within 2 seconds
- **SC-002**: PMs can add new knowledge through supported input methods (text, file) and see it indexed within one rebuild cycle
- **SC-003**: The vector index can be completely rebuilt from source Markdown files, ensuring no knowledge is lost if the index is deleted
- **SC-004**: 90% of test queries return expected results in the top-3 (recall@3 >= 0.90)
- **SC-005**: Users can filter search results by metadata (airline, route, cabin) and receive only matching results
- **SC-006**: Statistics provide complete visibility into KB composition, with breakdowns by type, category, and confidence level

## Assumptions

- This is a hackathon prototype for internal PM team use, not production-grade (no scale, high security, or uptime requirements)
- Hosting on free tier (Render free tier acceptable); data may be transient between deployments
- Chroma or equivalent vector database will be used (agent choice acceptable)
- Embedding model selection is delegated to implementation (agent choice acceptable)
- PMs have technical familiarity to use a CLI or simple web console
- Initial knowledge content will be manually seeded before launch

## Scope Boundaries

**In Scope:**
- Markdown-based knowledge storage with YAML frontmatter
- Vector index generation and semantic search
- CLI console for query, ingest, rebuild, stats
- Basic provenance and licensing tracking
- Simple evaluation framework
- Cloud hosting for prototype access
- Two starter templates (airline_premium_fare, hack)

**Out of Scope:**
- Production-grade security (enterprise auth, rigorous access control)
- High availability or uptime guarantees
- Large-scale performance optimization
- Real-time synchronization (manual rebuild is acceptable)
- Complex deduplication logic
- Full content management workflow (approval, versioning beyond status field)
- URL ingestion (deferred; use "export to PDF and ingest" workflow for web content)
