// API Request/Response Types

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  version: string;
}

export interface QueryRequest {
  text: string;
  k: number;
  filters?: Record<string, unknown>;
}

export interface ChunkResult {
  chunk_id: string;
  kb_id: string;
  title: string;
  text: string;
  score: number;
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

export interface QueryResponse {
  query: string;
  total_results: number;
  results: ChunkResult[];
}

export interface StatsResponse {
  document_count: number;
  chunk_count: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  by_confidence: Record<string, number>;
  by_status: Record<string, number>;
  index_metadata: Record<string, unknown>;
}

export interface RebuildResponse {
  success: boolean;
  documents_processed: number;
  chunks_indexed: number;
  duration_seconds: number;
  errors: string[];
}

export interface IngestRequest {
  content_type: "text" | "txt" | "pdf" | "html";
  content: string;
  filename?: string;
}

export interface IngestResponse {
  success: boolean;
  kb_id: string;
  file_path: string;
  title: string;
  chunk_count: number;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// Frontend State Types

export interface AppState {
  apiUrl: string;
  isConnected: boolean;
  connectionError?: string;
}

export interface QueryState {
  searchText: string;
  k: number;
  isLoading: boolean;
  results: ChunkResult[];
  error?: string;
  selectedResult?: ChunkResult;
}

export interface IngestState {
  mode: "text" | "file";
  textContent: string;
  file?: File;
  isIngesting: boolean;
  result?: IngestResponse;
  error?: string;
}

export interface StatsState {
  isLoading: boolean;
  stats?: StatsResponse;
  error?: string;
}

export interface AdminState {
  isRebuilding: boolean;
  rebuildResult?: RebuildResponse;
  error?: string;
}
