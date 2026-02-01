# KB Console - Requirements Checklist

## User Stories

### US1 - Query Knowledge Base (P1)
- [ ] Query form with text input field
- [ ] Adjustable k parameter (1-10) with slider or input
- [ ] Submit button triggers API call
- [ ] Results display chunk text
- [ ] Results display similarity score
- [ ] Results display source document ID
- [ ] Clickable results show full metadata
- [ ] Connection error handling with user message

### US2 - Ingest New Content (P2)
- [ ] Text area for pasting content
- [ ] File upload input accepting .txt
- [ ] File upload input accepting .pdf
- [ ] File upload input accepting .html/.htm
- [ ] Ingest button triggers API call
- [ ] Success confirmation shows kb_id
- [ ] Success confirmation shows file path
- [ ] Error handling for failed ingestion

### US3 - View Database Stats (P3)
- [ ] Stats page/section accessible from nav
- [ ] Display total document count
- [ ] Display total chunk count
- [ ] Display breakdown by status
- [ ] Display breakdown by type
- [ ] Display breakdown by confidence
- [ ] Empty state message when no documents

### US4 - Rebuild Index (P4)
- [ ] Rebuild button on admin section
- [ ] Progress indicator during rebuild
- [ ] Success message with summary
- [ ] Concurrent rebuild prevention
- [ ] Error handling with details

## Functional Requirements

- [ ] FR-001: Query interface with text and k parameter
- [ ] FR-002: Results show chunk text, score, metadata
- [ ] FR-003: Text ingestion form
- [ ] FR-004: File upload for txt/pdf/html/htm
- [ ] FR-005: Real-time stats display
- [ ] FR-006: Rebuild action with progress
- [ ] FR-007: Backpack design system components
- [ ] FR-008: GitHub Pages deployable
- [ ] FR-009: Configurable API base URL
- [ ] FR-010: Graceful error handling
- [ ] FR-011: Desktop responsive layout

## Non-Functional Requirements

- [ ] NFR-001: Page load < 3 seconds
- [ ] NFR-002: Query display < 2 seconds
- [ ] NFR-003: Backpack design guidelines followed

## Success Criteria

- [ ] SC-001: Query in 3 clicks from landing
- [ ] SC-002: Ingest in 2 clicks from landing
- [ ] SC-003: Lighthouse accessibility 80+
- [ ] SC-004: No Backpack console errors
- [ ] SC-005: GitHub Pages deployment works
- [ ] SC-006: All errors show friendly messages

## Edge Cases

- [ ] API unreachable shows connection error
- [ ] Zero results shows "no documents found"
- [ ] Large content (>100KB) shows warning
- [ ] Corrupt PDF shows error, no partial file
- [ ] Concurrent rebuild/query works correctly
