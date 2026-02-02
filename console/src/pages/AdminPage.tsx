import { useState } from 'react';
import { RebuildButton } from '../components/RebuildButton';
import { RebuildSummary } from '../components/RebuildSummary';
import { ErrorBanner } from '../components/ErrorBanner';
import { api, API_URL } from '../services/api';
import type { RebuildResponse, ApiError } from '../types';

type RebuildSource = 'github' | 'local';

export function AdminPage() {
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [result, setResult] = useState<RebuildResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rebuildSource, setRebuildSource] = useState<RebuildSource>('github');
  const [apiKey, setApiKey] = useState(() => {
    // Load from localStorage if available
    return localStorage.getItem('flightskb_api_key') || '';
  });

  const handleApiKeyChange = (value: string) => {
    setApiKey(value);
    // Persist to localStorage
    if (value) {
      localStorage.setItem('flightskb_api_key', value);
    } else {
      localStorage.removeItem('flightskb_api_key');
    }
  };

  const handleRebuild = async () => {
    if (isRebuilding) return; // Prevent concurrent rebuilds

    if (!apiKey.trim()) {
      setError('API key is required for rebuild operations.');
      return;
    }

    setIsRebuilding(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.rebuild(apiKey, rebuildSource);
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

      {/* API Key input */}
      <div className="card">
        <h3 style={{ margin: '0 0 8px 0' }}>API Key</h3>
        <p style={{ margin: '0 0 12px 0', color: '#68697f' }}>
          Required for admin operations (rebuild, ingest).
        </p>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => handleApiKeyChange(e.target.value)}
          placeholder="Enter your API key"
          style={{
            width: '100%',
            padding: '10px 12px',
            border: '1px solid #c1c7cf',
            borderRadius: '4px',
            fontSize: '14px',
            boxSizing: 'border-box',
          }}
        />
        <p style={{ margin: '8px 0 0 0', fontSize: '0.75rem', color: '#68697f' }}>
          Stored in browser localStorage for convenience.
        </p>
      </div>

      <div className="card" style={{ marginTop: '16px' }}>
        <h3 style={{ margin: '0 0 8px 0' }}>Rebuild Vector Index</h3>
        <p style={{ margin: '0 0 16px 0', color: '#68697f' }}>
          Re-process all knowledge base documents and regenerate vector embeddings.
          Use this after manually editing markdown files or to recover from index corruption.
        </p>

        {/* Rebuild source selector */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
            Rebuild Source
          </label>
          <div style={{ display: 'flex', gap: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="rebuildSource"
                value="github"
                checked={rebuildSource === 'github'}
                onChange={() => setRebuildSource('github')}
                disabled={isRebuilding}
              />
              <span>GitHub (recommended)</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="rebuildSource"
                value="local"
                checked={rebuildSource === 'local'}
                onChange={() => setRebuildSource('local')}
                disabled={isRebuilding}
              />
              <span>Local filesystem</span>
            </label>
          </div>
          <p style={{ margin: '8px 0 0 0', fontSize: '0.8rem', color: '#68697f' }}>
            {rebuildSource === 'github'
              ? 'Fetches all knowledge files from GitHub repository. Best for hosted deployments.'
              : 'Uses local knowledge/ directory. Best for local development.'}
          </p>
        </div>

        {isRebuilding && (
          <div className="warning-banner" style={{ marginBottom: '16px' }}>
            Index rebuild in progress from {rebuildSource === 'github' ? 'GitHub' : 'local files'}. This may take a few moments depending on the size of your knowledge base.
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
