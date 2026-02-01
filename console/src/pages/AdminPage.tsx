import { useState } from 'react';
import { RebuildButton } from '../components/RebuildButton';
import { RebuildSummary } from '../components/RebuildSummary';
import { ErrorBanner } from '../components/ErrorBanner';
import { api, API_URL } from '../services/api';
import type { RebuildResponse, ApiError } from '../types';

export function AdminPage() {
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [result, setResult] = useState<RebuildResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRebuild = async () => {
    if (isRebuilding) return; // Prevent concurrent rebuilds

    setIsRebuilding(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.rebuild();
      setResult(response);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to rebuild index. Please try again.');
    } finally {
      setIsRebuilding(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Admin Panel</h2>
        <p className="page-description">
          Administrative operations for the knowledge base.
        </p>
      </div>

      <div className="card">
        <h3 style={{ margin: '0 0 8px 0' }}>Rebuild Vector Index</h3>
        <p style={{ margin: '0 0 16px 0', color: '#68697f' }}>
          Re-process all knowledge base documents and regenerate vector embeddings.
          Use this after manually editing markdown files or to recover from index corruption.
        </p>

        {isRebuilding && (
          <div className="warning-banner" style={{ marginBottom: '16px' }}>
            Index rebuild in progress. This may take a few moments depending on the size of your knowledge base.
          </div>
        )}

        <RebuildButton onClick={handleRebuild} isLoading={isRebuilding} />
      </div>

      {error && (
        <div style={{ marginTop: '16px' }}>
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {result && (
        <div style={{ marginTop: '16px' }}>
          <RebuildSummary result={result} />
        </div>
      )}

      <div className="card" style={{ marginTop: '24px' }}>
        <h3 style={{ margin: '0 0 8px 0' }}>API Configuration</h3>
        <p style={{ margin: '0 0 16px 0', color: '#68697f' }}>
          Current API endpoint configuration.
        </p>
        <div style={{ background: '#f1f2f8', padding: '12px', borderRadius: '4px', fontFamily: 'monospace' }}>
          {API_URL}
        </div>
        <p style={{ margin: '12px 0 0 0', fontSize: '0.875rem', color: '#68697f' }}>
          To change the API URL, add <code>?api=https://your-api.com</code> to the URL or set the <code>VITE_API_URL</code> environment variable.
        </p>
      </div>
    </div>
  );
}
