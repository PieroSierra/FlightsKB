# Implementation Plan: KB Console

**Branch**: `002-kb-console` | **Date**: 2026-02-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-kb-console/spec.md`

## Summary

Build a React-based web console using Skyscanner Backpack design system that provides a visual interface for querying the knowledge base, ingesting new content, viewing statistics, and rebuilding the index. The console will be deployed as a static site on GitHub Pages and communicate with the existing FastAPI backend via HTTP/JSON.

## Technical Context

**Language/Version**: TypeScript 5.3+ with React 18.2+
**Primary Dependencies**: @skyscanner/backpack-web v41.9.0, Vite 5.0, react-router-dom 6.x
**Storage**: N/A (frontend only - uses backend API)
**Testing**: Vitest + React Testing Library
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web application (frontend added to existing backend)
**Performance Goals**: Page load <3s, query display <2s (excluding API latency)
**Constraints**: Static hosting (GitHub Pages), cross-origin API calls (CORS required)
**Scale/Scope**: 4 pages (query, ingest, stats, admin), ~15 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution defined. Following standard practices:
- ✅ Reusing existing backend API (no duplication)
- ✅ Adding frontend to existing monorepo (not creating separate repo)
- ✅ Using specified design system (Backpack)
- ✅ Static deployment (GitHub Pages - no new infrastructure)

## Project Structure

### Documentation (this feature)

```text
specs/002-kb-console/
├── plan.md              # This file
├── research.md          # Technology decisions (React, Vite, Backpack)
├── data-model.md        # API contracts and frontend state models
├── quickstart.md        # Development and deployment guide
├── contracts/           # New API endpoint spec
│   └── openapi-ingest.yaml
└── tasks.md             # Phase 2 output (from /speckit.tasks)
```

### Source Code (repository root)

```text
# Frontend (new)
console/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── SearchForm.tsx
│   │   ├── ResultCard.tsx
│   │   ├── StatsDisplay.tsx
│   │   └── ErrorBanner.tsx
│   ├── pages/           # Route pages
│   │   ├── QueryPage.tsx
│   │   ├── IngestPage.tsx
│   │   ├── StatsPage.tsx
│   │   └── AdminPage.tsx
│   ├── services/        # API client
│   │   └── api.ts
│   ├── types/           # TypeScript interfaces
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts

# Backend (additions)
src/api/
└── routes.py            # Add /ingest endpoint

# CI/CD (new)
.github/workflows/
└── deploy-console.yml   # GitHub Pages deployment
```

**Structure Decision**: Adding `console/` directory for frontend, keeping backend in existing `src/`. This separates concerns while maintaining single repository.

## Complexity Tracking

No violations to justify - design follows minimal complexity:
- Single frontend project (no micro-frontends)
- React hooks for state (no Redux/Zustand)
- Fetch API for HTTP (no Axios)
- Single deployment target (GitHub Pages)

## Key Implementation Notes

### Backend Changes Required
1. Add CORS middleware to FastAPI for GitHub Pages origin
2. Add `/ingest` endpoint using existing `IngestService`

### Frontend Architecture
1. React Router for client-side routing
2. Environment-based API URL configuration
3. Backpack components for consistent UI
4. Error boundary for graceful failure handling

### Deployment Strategy
1. GitHub Actions workflow on push to main
2. Build React app with Vite
3. Deploy `dist/` to `gh-pages` branch
4. Console available at `https://pierosierra.github.io/FlightsKB/`
