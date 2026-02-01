# Data Model: KB Console

**Branch**: `002-kb-console`
**Created**: 2026-02-01

## Overview

The KB Console is a frontend application that communicates with the existing Flights KB API. This document defines the API contracts and frontend state models.

## API Contracts

### Existing Endpoints (no changes)

#### GET /health
```typescript
interface HealthResponse {
  status: "healthy" | "unhealthy";
  version: string;
}
```

#### POST /query
```typescript
interface QueryRequest {
  text: string;      // 1-1000 chars
  k: number;         // 1-50, default 5
  filters?: Record<string, unknown>;
}

interface ChunkResult {
  chunk_id: string;
  kb_id: string;
  title: string;
  text: string;
  score: number;     // 0.0-1.0 similarity
  metadata: {
    confidence?: "high" | "medium" | "low";
    type?: string;
    applies_to?: string;
    source?: {
      kind: string;
      name?: string;
      url?: string;
    };
  };
  file_path?: string;
}

interface QueryResponse {
  query: string;
  total_results: number;
  results: ChunkResult[];
}
```

#### GET /stats
```typescript
interface StatsResponse {
  document_count: number;
  chunk_count: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  by_confidence: Record<string, number>;
  by_status: Record<string, number>;
  index_metadata: Record<string, unknown>;
}
```

#### POST /rebuild
```typescript
interface RebuildResponse {
  success: boolean;
  documents_processed: number;
  chunks_indexed: number;
  duration_seconds: number;
  errors: string[];
}
```

### New Endpoint (to be added)

#### POST /ingest
```typescript
interface IngestRequest {
  content_type: "text" | "txt" | "pdf" | "html";
  content: string;           // Raw text or base64 for binary
  filename?: string;         // Original filename for reference
}

interface IngestResponse {
  success: boolean;
  kb_id: string;             // Generated KB ID
  file_path: string;         // Path to created .md file
  title: string;             // Extracted/generated title
  chunk_count: number;       // Number of chunks created
}

interface IngestError {
  error: "INVALID_CONTENT" | "PARSE_FAILED" | "STORAGE_ERROR";
  message: string;
  details?: Record<string, unknown>;
}
```

## Frontend State Models

### Application State
```typescript
interface AppState {
  apiUrl: string;
  isConnected: boolean;
  connectionError?: string;
}
```

### Query Page State
```typescript
interface QueryState {
  searchText: string;
  k: number;
  isLoading: boolean;
  results: ChunkResult[];
  error?: string;
  selectedResult?: ChunkResult;
}
```

### Ingest Page State
```typescript
interface IngestState {
  mode: "text" | "file";
  textContent: string;
  file?: File;
  isIngesting: boolean;
  result?: IngestResponse;
  error?: string;
}
```

### Stats Page State
```typescript
interface StatsState {
  isLoading: boolean;
  stats?: StatsResponse;
  error?: string;
}
```

### Admin Page State
```typescript
interface AdminState {
  isRebuilding: boolean;
  rebuildResult?: RebuildResponse;
  error?: string;
}
```

## Error Responses

All API errors follow this format:
```typescript
interface ApiError {
  error: string;      // Error code (e.g., "INDEX_UNAVAILABLE")
  message: string;    // Human-readable message
  details?: Record<string, unknown>;
}
```

Common error codes:
| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INDEX_UNAVAILABLE` | 503 | ChromaDB not accessible |
| `INVALID_REQUEST` | 400 | Malformed request body |
| `UNAUTHORIZED` | 401 | Missing/invalid API key |
| `REBUILD_FAILED` | 500 | Index rebuild error |
| `PARSE_FAILED` | 422 | File parsing error |
| `CONTENT_TOO_LARGE` | 413 | Content exceeds size limit |

## Validation Rules

### Query Validation
- `text`: Required, 1-1000 characters
- `k`: Optional, 1-50, defaults to 5

### Ingest Validation
- `content_type`: Required, one of: text, txt, pdf, html
- `content`: Required, max 5MB for files, 100KB for text
- `filename`: Optional, for display purposes

## State Transitions

### Query Flow
```
IDLE → LOADING → SUCCESS (with results)
                → ERROR (display message, allow retry)
```

### Ingest Flow
```
IDLE → INGESTING → SUCCESS (show kb_id, offer another)
                 → ERROR (show message, preserve input)
```

### Rebuild Flow
```
IDLE → REBUILDING → SUCCESS (show summary)
                  → ERROR (show details)
```

## File Format Reference

Ingested content creates Markdown files with this structure:
```yaml
---
kb_id: ingest-{uuid8}
title: "{extracted or generated title}"
type: ingested
status: draft
confidence: medium
created: "{date}"
updated: "{date}"
source:
  kind: internal
  name: manual
  url: null
  retrieved: null
---

## Section 1

{content}
```
