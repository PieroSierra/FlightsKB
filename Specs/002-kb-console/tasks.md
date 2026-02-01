# Tasks: KB Console

**Input**: Design documents from `/specs/002-kb-console/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - tests omitted per template guidance.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in all descriptions

## Path Conventions

- **Frontend**: `console/src/` (new React app)
- **Backend**: `src/api/` (existing FastAPI)
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Vite React TypeScript project in console/ with `npm create vite@latest console -- --template react-ts`
- [x] T002 Install Backpack dependencies: @skyscanner/backpack-web, @skyscanner/bpk-foundations-web in console/package.json
- [x] T003 [P] Install routing dependency: react-router-dom in console/package.json
- [x] T004 [P] Configure Vite for GitHub Pages deployment in console/vite.config.ts (set base path)
- [x] T005 [P] Create TypeScript interfaces from data-model.md in console/src/types/index.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Add CORS middleware to FastAPI backend in src/api/app.py (allow GitHub Pages origin)
- [x] T007 Create API client service with configurable base URL in console/src/services/api.ts
- [x] T008 [P] Create Layout component with navigation header in console/src/components/Layout.tsx
- [x] T009 [P] Create ErrorBanner component for API error display in console/src/components/ErrorBanner.tsx
- [x] T010 Setup React Router with 4 routes (/, /ingest, /stats, /admin) in console/src/App.tsx
- [x] T011 Create main entry point with BrowserRouter in console/src/main.tsx
- [x] T012 [P] Create index.html with Backpack CSS imports in console/index.html

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Query Knowledge Base (Priority: P1) 🎯 MVP

**Goal**: Search the knowledge base through a web interface with configurable k parameter

**Independent Test**: Enter "business class tips" with k=3, verify 3 ranked results display with chunk text, similarity scores, and source document IDs

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement query() function in API client in console/src/services/api.ts
- [x] T014 [P] [US1] Create SearchForm component with text input and k selector in console/src/components/SearchForm.tsx
- [x] T015 [P] [US1] Create ResultCard component displaying chunk text, score, and metadata in console/src/components/ResultCard.tsx
- [x] T016 [US1] Create QueryPage with search form, results list, and loading state in console/src/pages/QueryPage.tsx
- [x] T017 [US1] Add result detail modal showing full metadata (applies_to, confidence, source) in console/src/pages/QueryPage.tsx
- [x] T018 [US1] Add error handling for API unavailable state with user-friendly message in console/src/pages/QueryPage.tsx
- [x] T019 [US1] Add "no results found" empty state display in console/src/pages/QueryPage.tsx

**Checkpoint**: Query functionality fully operational - can search and view results independently

---

## Phase 4: User Story 2 - Ingest New Content (Priority: P2)

**Goal**: Paste or upload content (text, PDF, HTML) through the web interface to add new knowledge

**Independent Test**: Paste text about flight tips, click Ingest, verify new .md file created in knowledge/inbox/ with proper frontmatter

### Backend Extension for User Story 2

- [x] T020 [US2] Add /ingest POST endpoint to FastAPI backend in src/api/routes.py
- [x] T021 [US2] Add request/response models for IngestRequest, IngestResponse in src/api/routes.py
- [x] T022 [US2] Implement base64 decoding for file content in /ingest endpoint in src/api/routes.py
- [x] T023 [US2] Add file size validation (100KB text, 5MB files) in src/api/routes.py

### Frontend Implementation for User Story 2

- [x] T024 [P] [US2] Implement ingest() function in API client in console/src/services/api.ts
- [x] T025 [P] [US2] Create TextIngestForm component with textarea in console/src/components/TextIngestForm.tsx
- [x] T026 [P] [US2] Create FileUploadForm component accepting .txt, .pdf, .html, .htm in console/src/components/FileUploadForm.tsx
- [x] T027 [US2] Create IngestPage with tab toggle between text and file modes in console/src/pages/IngestPage.tsx
- [x] T028 [US2] Add success confirmation showing kb_id and file_path in console/src/pages/IngestPage.tsx
- [x] T029 [US2] Add error handling for parse failures and size limits in console/src/pages/IngestPage.tsx
- [x] T030 [US2] Add file type validation on client-side before upload in console/src/components/FileUploadForm.tsx

**Checkpoint**: Ingest functionality complete - can add content via text or file upload independently

---

## Phase 5: User Story 3 - View Database Stats (Priority: P3)

**Goal**: Display knowledge base statistics including document count, chunk count, and breakdowns

**Independent Test**: Navigate to /stats, verify document count, chunk count, and breakdown by status/type/confidence displayed

### Implementation for User Story 3

- [x] T031 [P] [US3] Implement getStats() function in API client in console/src/services/api.ts
- [x] T032 [P] [US3] Create StatsDisplay component with summary cards in console/src/components/StatsDisplay.tsx
- [x] T033 [P] [US3] Create BreakdownTable component for category breakdowns in console/src/components/BreakdownTable.tsx
- [x] T034 [US3] Create StatsPage with stats display and auto-refresh in console/src/pages/StatsPage.tsx
- [x] T035 [US3] Add empty state message for zero documents in console/src/pages/StatsPage.tsx
- [x] T036 [US3] Add loading skeleton while stats fetching in console/src/pages/StatsPage.tsx

**Checkpoint**: Stats page complete - can view knowledge base health independently

---

## Phase 6: User Story 4 - Rebuild Index (Priority: P4)

**Goal**: Trigger full index rebuild from web interface with progress feedback

**Independent Test**: Click "Rebuild Index", wait for completion, verify summary shows documents processed and chunks indexed

### Implementation for User Story 4

- [x] T037 [P] [US4] Implement rebuild() function in API client in console/src/services/api.ts
- [x] T038 [P] [US4] Create RebuildButton component with loading state in console/src/components/RebuildButton.tsx
- [x] T039 [P] [US4] Create RebuildSummary component showing results in console/src/components/RebuildSummary.tsx
- [x] T040 [US4] Create AdminPage with rebuild action and results display in console/src/pages/AdminPage.tsx
- [x] T041 [US4] Add progress indicator during rebuild operation in console/src/pages/AdminPage.tsx
- [x] T042 [US4] Add error handling for rebuild failures with details in console/src/pages/AdminPage.tsx
- [x] T043 [US4] Add rebuild-in-progress state blocking concurrent rebuilds in console/src/pages/AdminPage.tsx

**Checkpoint**: Admin functionality complete - can trigger and monitor index rebuilds independently

---

## Phase 7: Polish & Deployment

**Purpose**: Production readiness and deployment automation

- [x] T044 [P] Create GitHub Actions workflow for console deployment in .github/workflows/deploy-console.yml
- [x] T045 [P] Add environment variable for API URL in console/.env.example
- [x] T046 [P] Update console/README.md with development and deployment instructions
- [x] T047 Verify all Backpack components render without console errors
- [ ] T048 Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] T049 Validate Lighthouse accessibility score meets 80+ target
- [ ] T050 Run quickstart.md validation end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - Stories can proceed in parallel if team capacity allows
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational + backend /ingest endpoint (T020-T023) - Independent of US1
- **User Story 3 (P3)**: Depends only on Foundational - No dependencies on other stories
- **User Story 4 (P4)**: Depends only on Foundational - No dependencies on other stories

### Within Each User Story

- API client functions before UI components
- Reusable components before page components
- Core functionality before error handling
- Error handling before polish

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003, T004, T005 can run in parallel
```

**Phase 2 (Foundational)**:
```
T008, T009, T012 can run in parallel (after T006, T007)
```

**Phase 3 (US1)**:
```
T013, T014, T015 can run in parallel
```

**Phase 4 (US2)**:
```
T024, T025, T026 can run in parallel (frontend)
Backend tasks T020-T023 must be sequential
```

**Phase 5 (US3)**:
```
T031, T032, T033 can run in parallel
```

**Phase 6 (US4)**:
```
T037, T038, T039 can run in parallel
```

**Phase 7 (Polish)**:
```
T044, T045, T046 can run in parallel
```

---

## Parallel Example: User Story 1

```bash
# Launch all independent tasks for User Story 1 together:
Task: "Implement query() function in console/src/services/api.ts"
Task: "Create SearchForm component in console/src/components/SearchForm.tsx"
Task: "Create ResultCard component in console/src/components/ResultCard.tsx"

# Then sequentially:
Task: "Create QueryPage in console/src/pages/QueryPage.tsx" (uses above components)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (5 tasks)
2. Complete Phase 2: Foundational (7 tasks)
3. Complete Phase 3: User Story 1 (7 tasks)
4. **STOP and VALIDATE**: Test query functionality independently
5. Deploy to GitHub Pages for demo

**MVP Total**: 19 tasks

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → Deploy (MVP! Query works)
3. Add User Story 2 → Test → Deploy (Can add content)
4. Add User Story 3 → Test → Deploy (Can view stats)
5. Add User Story 4 → Test → Deploy (Can rebuild index)

### Full Implementation

**Total Tasks**: 50
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1 Query): 7 tasks
- Phase 4 (US2 Ingest): 11 tasks (4 backend + 7 frontend)
- Phase 5 (US3 Stats): 6 tasks
- Phase 6 (US4 Rebuild): 7 tasks
- Phase 7 (Polish): 7 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story independently testable after completion
- US2 requires backend changes (T020-T023) before frontend can test
- Commit after each task or logical group
- CORS (T006) must complete before any frontend API calls work
