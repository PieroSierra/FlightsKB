# Feature Specification: KB Console

**Feature Branch**: `002-kb-console`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "Console - ability to inspect DB -> query DB (e.g. K=3, text ="business class") returns vectors & chunks --- ability to feed it new KB as a (large) block of text or PDF or .HTM which it will chunk and store into .MD --- ability to rebuild DB from KB --- DB stats and health index. It should run as a website (hosted on GH pages maybe?) and use the Skyscanner design system Backpack"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Knowledge Base (Priority: P1)

As a hackathon participant, I want to search the knowledge base through a web interface so I can quickly find relevant flight tips and information without using the command line.

**Why this priority**: This is the primary read operation and most frequently used feature. Without query capability, the console has no practical value.

**Independent Test**: Can be fully tested by entering a search query like "business class tips" with k=3 and verifying that results display with chunk text, similarity scores, and source document references.

**Acceptance Scenarios**:

1. **Given** the console is loaded, **When** I enter "business class" in the query field and set k=3, **Then** I see 3 ranked results with chunk text, similarity scores, and source document IDs
2. **Given** query results are displayed, **When** I click on a result, **Then** I can see the full chunk content and metadata (applies_to, confidence, source)
3. **Given** the backend API is unreachable, **When** I submit a query, **Then** I see a clear error message indicating the connection issue

---

### User Story 2 - Ingest New Content (Priority: P2)

As a hackathon participant, I want to paste or upload content (text, PDF, HTML) through the web interface so I can quickly add new knowledge without manually creating Markdown files.

**Why this priority**: Content ingestion is the primary write operation. It enables growing the knowledge base through the UI, which is essential for a complete workflow but secondary to querying existing content.

**Independent Test**: Can be fully tested by pasting a block of text about flight tips, clicking ingest, and verifying a new .md file appears in `knowledge/inbox/` with proper YAML frontmatter.

**Acceptance Scenarios**:

1. **Given** I am on the ingest page, **When** I paste a large block of text and click "Ingest", **Then** the system creates a new Markdown file in `knowledge/inbox/` with generated YAML frontmatter
2. **Given** I am on the ingest page, **When** I upload a .txt file, **Then** the content is processed and stored as Markdown
3. **Given** I am on the ingest page, **When** I upload a .pdf file, **Then** the text is extracted and stored as Markdown
4. **Given** I am on the ingest page, **When** I upload a .html/.htm file, **Then** the text content is extracted (tags stripped) and stored as Markdown
5. **Given** ingestion completes successfully, **When** I view the result, **Then** I see a confirmation with the generated file path and kb_id

---

### User Story 3 - View Database Stats (Priority: P3)

As a hackathon participant, I want to see statistics about the knowledge base so I can understand its size, health, and content distribution.

**Why this priority**: Stats provide visibility into the system state but are not required for core query/ingest operations. Useful for debugging and demonstrations.

**Independent Test**: Can be fully tested by loading the stats page and verifying document count, chunk count, and breakdown by status/type/confidence are displayed correctly.

**Acceptance Scenarios**:

1. **Given** the console is loaded, **When** I navigate to the stats page, **Then** I see total document count, chunk count, and index size
2. **Given** stats are displayed, **When** I view detailed breakdowns, **Then** I see counts grouped by status (draft/review/published), type (tip/guide/policy), and confidence (high/medium/low)
3. **Given** the knowledge base is empty, **When** I view stats, **Then** I see zeros and a message indicating no documents indexed

---

### User Story 4 - Rebuild Index (Priority: P4)

As a hackathon participant, I want to trigger a full index rebuild from the web interface so I can refresh embeddings after manually editing knowledge files.

**Why this priority**: Rebuild is an administrative operation needed occasionally when knowledge files are edited outside the console. Lower priority because ingestion automatically updates the index.

**Independent Test**: Can be fully tested by clicking "Rebuild Index", waiting for completion, and verifying the stats show updated chunk counts matching current knowledge files.

**Acceptance Scenarios**:

1. **Given** I am on the admin page, **When** I click "Rebuild Index", **Then** I see a progress indicator while the rebuild runs
2. **Given** rebuild completes successfully, **When** I view the result, **Then** I see a summary showing documents processed and chunks indexed
3. **Given** rebuild is in progress, **When** I try to start another rebuild, **Then** I see a message indicating rebuild is already running
4. **Given** an error occurs during rebuild, **When** the process fails, **Then** I see a clear error message with details

---

### Edge Cases

- What happens when the API backend is not running? → Display connection error with instructions to start the server
- What happens when query returns zero results? → Display "No matching documents found" message
- What happens when ingesting extremely large content (>100KB)? → Accept and process, but show warning about chunking
- What happens when PDF extraction fails (corrupt file)? → Display error message, do not create partial file
- What happens when rebuild is triggered during an active query? → Allow concurrent operation (ChromaDB handles locking)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web-based query interface that accepts search text and k parameter (1-10)
- **FR-002**: System MUST display query results with chunk text, similarity score, and source document metadata
- **FR-003**: System MUST provide a content ingestion form accepting plain text input
- **FR-004**: System MUST support file upload for .txt, .pdf, .html, and .htm formats
- **FR-005**: System MUST display real-time statistics including document count, chunk count, and breakdowns
- **FR-006**: System MUST provide a rebuild index action with progress feedback
- **FR-007**: System MUST use Skyscanner Backpack design system for all UI components
- **FR-008**: System MUST be deployable as a static site on GitHub Pages
- **FR-009**: System MUST communicate with the existing FastAPI backend at configurable base URL
- **FR-010**: System MUST handle API errors gracefully with user-friendly messages
- **FR-011**: System MUST be responsive and work on desktop browsers (mobile optimization is optional)

### Non-Functional Requirements

- **NFR-001**: Console MUST load initial page within 3 seconds on standard broadband
- **NFR-002**: Query results MUST display within 2 seconds of submission (excluding API latency)
- **NFR-003**: UI MUST follow Backpack design guidelines for consistency with Skyscanner products

### Key Entities

- **QueryRequest**: Search text, k parameter (number of results)
- **QueryResult**: Chunk ID, text content, similarity score, source document metadata
- **IngestRequest**: Content type (text/file), raw content or file data
- **IngestResponse**: Generated kb_id, file path, chunk count
- **StatsResponse**: Document count, chunk count, breakdowns by status/type/confidence
- **RebuildResponse**: Success status, documents processed, chunks indexed, duration

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can execute a query and view results within 3 clicks from landing page
- **SC-002**: Users can ingest new text content within 2 clicks from landing page
- **SC-003**: Console passes Lighthouse accessibility score of 80+
- **SC-004**: All Backpack components render correctly without console errors
- **SC-005**: Console deploys successfully to GitHub Pages via automated workflow
- **SC-006**: 100% of API error states display user-friendly messages (no raw JSON errors shown)
