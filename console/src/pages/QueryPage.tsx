import { useState } from 'react';
import { SearchForm } from '../components/SearchForm';
import { ResultCard } from '../components/ResultCard';
import { ErrorBanner } from '../components/ErrorBanner';
import { api } from '../services/api';
import type { ChunkResult, ApiError } from '../types';

export function QueryPage() {
  const [results, setResults] = useState<ChunkResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ChunkResult | null>(null);

  const handleSearch = async (text: string, k: number) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await api.query({ text, k });
      setResults(response.results);
    } catch (err) {
      const apiError = err as ApiError;
      if (apiError.message) {
        setError(apiError.message);
      } else {
        setError('Unable to connect to the API. Please ensure the backend server is running.');
      }
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Query Knowledge Base</h2>
        <p className="page-description">
          Search for flight tips, guides, and policies using natural language.
        </p>
      </div>

      <SearchForm onSearch={handleSearch} isLoading={isLoading} />

      {error && (
        <div style={{ marginTop: '16px' }}>
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {isLoading && (
        <div className="empty-state">
          <span className="spinner spinner--large" />
          <p style={{ marginTop: '16px' }}>Searching knowledge base...</p>
        </div>
      )}

      {!isLoading && hasSearched && results.length === 0 && !error && (
        <div className="empty-state">
          <h3>No results found</h3>
          <p>Try adjusting your search terms or broadening your query.</p>
        </div>
      )}

      {!isLoading && results.length > 0 && (
        <div className="results-list" style={{ marginTop: '24px' }}>
          <h3>{results.length} result{results.length !== 1 ? 's' : ''} found</h3>
          {results.map((result) => (
            <ResultCard
              key={result.chunk_id}
              result={result}
              onClick={() => setSelectedResult(result)}
            />
          ))}
        </div>
      )}

      {selectedResult && (
        <div className="modal-overlay" onClick={() => setSelectedResult(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedResult.title}</h3>
              <button className="modal-close" onClick={() => setSelectedResult(null)}>
                ×
              </button>
            </div>

            <div className="metadata-item">
              <div className="metadata-label">Full Content</div>
              <div className="metadata-value" style={{ whiteSpace: 'pre-wrap' }}>
                {selectedResult.text}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="metadata-item">
                <div className="metadata-label">Chunk ID</div>
                <div className="metadata-value">{selectedResult.chunk_id}</div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">KB ID</div>
                <div className="metadata-value">{selectedResult.kb_id}</div>
              </div>

              <div className="metadata-item">
                <div className="metadata-label">Similarity Score</div>
                <div className="metadata-value">{Math.round(selectedResult.score * 100)}%</div>
              </div>

              {selectedResult.metadata.confidence && (
                <div className="metadata-item">
                  <div className="metadata-label">Confidence</div>
                  <div className="metadata-value">{selectedResult.metadata.confidence}</div>
                </div>
              )}

              {selectedResult.metadata.type && (
                <div className="metadata-item">
                  <div className="metadata-label">Type</div>
                  <div className="metadata-value">{selectedResult.metadata.type}</div>
                </div>
              )}

              {selectedResult.metadata.applies_to && (
                <div className="metadata-item">
                  <div className="metadata-label">Applies To</div>
                  <div className="metadata-value">{selectedResult.metadata.applies_to}</div>
                </div>
              )}

              {selectedResult.metadata.source && (
                <div className="metadata-item">
                  <div className="metadata-label">Source</div>
                  <div className="metadata-value">
                    {selectedResult.metadata.source.name || selectedResult.metadata.source.kind}
                    {selectedResult.metadata.source.url && (
                      <a
                        href={selectedResult.metadata.source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ marginLeft: '8px' }}
                      >
                        (link)
                      </a>
                    )}
                  </div>
                </div>
              )}

              {selectedResult.file_path && (
                <div className="metadata-item">
                  <div className="metadata-label">File Path</div>
                  <div className="metadata-value">{selectedResult.file_path}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
