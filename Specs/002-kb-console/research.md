# Research: KB Console

**Branch**: `002-kb-console`
**Created**: 2026-02-01

## Technology Decisions

### 1. Frontend Framework

**Decision**: React 18+ with Vite build tooling

**Rationale**:
- Backpack design system (`@skyscanner/backpack-web`) is React-based with 70+ components
- Vite provides fast development server and optimized static builds for GitHub Pages
- React's component model fits well with the query/ingest/stats/rebuild UI sections
- Static build output works perfectly with GitHub Pages hosting

**Alternatives Considered**:
| Option | Evaluated | Rejected Because |
|--------|-----------|------------------|
| Vanilla JS | Yes | Backpack components require React |
| Next.js | Yes | Overkill for static site, SSR not needed |
| Create React App | Yes | Deprecated, Vite is faster and modern |
| Vue/Svelte | Yes | Would require wrapping/porting Backpack components |

---

### 2. Design System

**Decision**: Skyscanner Backpack (`@skyscanner/backpack-web` v41.9.0)

**Rationale**:
- User requirement - specified in feature description
- Production-grade components (buttons, inputs, cards, modals, spinners)
- Consistent Skyscanner visual language
- Apache-2.0 license allows free use

**Key Components to Use**:
| Component | Use Case |
|-----------|----------|
| BpkInput | Query text field |
| BpkSelect | K parameter dropdown |
| BpkButton | Submit, Ingest, Rebuild actions |
| BpkCard | Search result display |
| BpkSpinner | Loading states |
| BpkBannerAlert | Error/success messages |
| BpkTextarea | Content ingestion input |
| BpkFileInput | File upload for pdf/txt/html |
| BpkProgress | Rebuild progress indicator |

**Dependencies**:
```
@skyscanner/backpack-web
@skyscanner/bpk-foundations-web
```

---

### 3. State Management

**Decision**: React hooks (useState, useReducer) - no external library

**Rationale**:
- Application state is simple: query results, stats, loading states
- No complex cross-component state sharing needed
- Keeps bundle size small for GitHub Pages
- React 18 built-in state is sufficient

**Alternatives Considered**:
- Redux: Overkill for 4 screens
- Zustand: Nice but unnecessary complexity
- React Query: Would be good but adds dependency weight

---

### 4. API Communication

**Decision**: Native fetch API with async/await

**Rationale**:
- Modern browsers have excellent fetch support
- No additional dependencies
- Simple request/response pattern matches our API
- Easy error handling with try/catch

**API Base URL Strategy**:
- Environment variable `VITE_API_URL` for build-time configuration
- Default to `http://localhost:8000` for local development
- Allow runtime override via URL parameter `?api=https://...`

---

### 5. Hosting & Deployment

**Decision**: GitHub Pages with GitHub Actions CI/CD

**Rationale**:
- Free static hosting
- Integrates with existing repository
- Automatic deployment on push to main
- Custom domain support if needed later

**Deployment Workflow**:
1. Push to `main` branch triggers workflow
2. `npm run build` creates `dist/` folder
3. Deploy `dist/` to `gh-pages` branch
4. Site available at `https://pierosierra.github.io/FlightsKB/`

**CORS Consideration**:
- GitHub Pages is static-only; API runs elsewhere
- FastAPI backend must enable CORS for GitHub Pages origin
- Add `CORSMiddleware` to allow cross-origin requests

---

### 6. Build & Development Tooling

**Decision**: Vite + TypeScript

**Rationale**:
- Vite: Fast HMR, optimized production builds, excellent React support
- TypeScript: Type safety for API contracts, better IDE support
- Both are modern standards for React development

**Build Output**:
- Single-page application in `dist/`
- Hash-based cache busting for assets
- `index.html` with client-side routing

---

### 7. Backend API Extension

**Decision**: Add `/ingest` endpoint to existing FastAPI backend

**Rationale**:
- Current API has `/query`, `/stats`, `/rebuild` but no `/ingest`
- Console requires API-based ingestion (can't write files from browser)
- Reuse existing `IngestService` from CLI

**New Endpoint**:
```
POST /ingest
Body: { "content_type": "text|txt|pdf|html", "content": "base64 or raw text" }
Response: { "kb_id": "...", "file_path": "...", "chunk_count": N }
```

---

### 8. File Upload Handling

**Decision**: Base64 encoding for file content

**Rationale**:
- Simple JSON API - no multipart form handling
- Works with existing content processing pipeline
- Small files expected (KB articles, not large documents)

**Size Limits**:
- Text input: 100KB max
- File upload: 5MB max (reasonable for PDF/HTML)

---

## Dependency Summary

### Frontend Dependencies
```json
{
  "@skyscanner/backpack-web": "^41.9.0",
  "@skyscanner/bpk-foundations-web": "latest",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0"
}
```

### Dev Dependencies
```json
{
  "@types/react": "^18.2.0",
  "@types/react-dom": "^18.2.0",
  "@vitejs/plugin-react": "^4.2.0",
  "typescript": "^5.3.0",
  "vite": "^5.0.0"
}
```

### Backend Addition
```python
# Add CORS support
fastapi[all]  # includes CORSMiddleware
```

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Which frontend framework? | React (required by Backpack) |
| Static vs server-rendered? | Static (GitHub Pages requirement) |
| State management? | React hooks (simple enough) |
| How to handle CORS? | Add CORSMiddleware to FastAPI |
| API for ingestion? | New `/ingest` endpoint needed |
| File upload approach? | Base64 in JSON body |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| CORS blocks API calls | FastAPI CORSMiddleware with explicit origins |
| Large bundle size | Tree-shake Backpack imports, code splitting |
| API unavailable | Clear error states, connection status indicator |
| File parsing fails | Server-side validation, user-friendly error messages |
| GitHub Pages caching | Hash-based filenames for cache busting |
