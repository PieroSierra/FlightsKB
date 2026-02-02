import type {
  QueryRequest,
  QueryResponse,
  StatsResponse,
  RebuildResponse,
  IngestRequest,
  IngestResponse,
  HealthResponse,
  ApiError,
  CategoriesResponse,
  FileTreeResponse,
  FileContentResponse,
} from '../types';

const getApiUrl = (): string => {
  // Check URL parameter first (allows override for testing)
  const params = new URLSearchParams(window.location.search);
  const urlParam = params.get('api');
  if (urlParam) return urlParam;

  // Then environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // Check if we're on Render (*.onrender.com) or other production host
  const hostname = window.location.hostname;
  if (hostname.endsWith('.onrender.com') || hostname !== 'localhost') {
    // In production, API is served from same origin under /api
    return window.location.origin;
  }

  // Default to localhost for development
  return 'http://localhost:8000';
};

const API_URL = getApiUrl();

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorData: ApiError;
      try {
        const data = await response.json();
        errorData = {
          error: data.detail?.error || 'API_ERROR',
          message: data.detail?.message || data.detail || response.statusText,
          details: data.detail?.details,
        };
      } catch {
        errorData = {
          error: 'API_ERROR',
          message: response.statusText,
        };
      }
      throw errorData;
    }

    return response.json();
  }

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/api/health');
  }

  async query(request: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>('/api/query', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getStats(): Promise<StatsResponse> {
    return this.request<StatsResponse>('/api/stats');
  }

  async rebuild(apiKey?: string, source?: 'github' | 'local'): Promise<RebuildResponse> {
    const headers: Record<string, string> = {};
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    return this.request<RebuildResponse>('/api/rebuild', {
      method: 'POST',
      headers,
      body: source ? JSON.stringify({ source }) : undefined,
    });
  }

  async ingest(request: IngestRequest, apiKey?: string): Promise<IngestResponse> {
    const headers: Record<string, string> = {};
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    return this.request<IngestResponse>('/api/ingest', {
      method: 'POST',
      body: JSON.stringify(request),
      headers,
    });
  }

  async getCategories(): Promise<CategoriesResponse> {
    return this.request<CategoriesResponse>('/api/categories');
  }

  async getFileTree(): Promise<FileTreeResponse> {
    return this.request<FileTreeResponse>('/api/files/tree');
  }

  async getFileContent(path: string): Promise<FileContentResponse> {
    return this.request<FileContentResponse>(`/api/files/content?path=${encodeURIComponent(path)}`);
  }
}

export const api = new ApiClient();
export { API_URL };
