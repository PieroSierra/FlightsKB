import { useState, useEffect } from 'react';
import { StatsDisplay } from '../components/StatsDisplay';
import { BreakdownTable } from '../components/BreakdownTable';
import { ErrorBanner } from '../components/ErrorBanner';
import { api } from '../services/api';
import type { StatsResponse, ApiError } from '../types';

export function StatsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getStats();
      setStats(response);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Unable to fetch statistics. Please ensure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 className="page-title">Database Statistics</h2>
          <p className="page-description">
            Overview of knowledge base contents and distribution.
          </p>
        </div>
        <button className="bpk-button" onClick={fetchStats} disabled={isLoading}>
          Refresh
        </button>
      </div>

      {error && (
        <div style={{ marginBottom: '24px' }}>
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {isLoading && (
        <div className="empty-state">
          <span className="spinner spinner--large" />
          <p style={{ marginTop: '16px' }}>Loading statistics...</p>
        </div>
      )}

      {!isLoading && stats && stats.document_count === 0 && (
        <div className="empty-state">
          <h3>No Documents Indexed</h3>
          <p>The knowledge base is empty. Add content using the Ingest page or rebuild the index.</p>
        </div>
      )}

      {!isLoading && stats && stats.document_count > 0 && (
        <>
          <StatsDisplay
            documentCount={stats.document_count}
            chunkCount={stats.chunk_count}
          />

          <div style={{ marginTop: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
            {Object.keys(stats.by_status).length > 0 && (
              <BreakdownTable title="By Status" data={stats.by_status} />
            )}
            {Object.keys(stats.by_type).length > 0 && (
              <BreakdownTable title="By Type" data={stats.by_type} />
            )}
            {Object.keys(stats.by_confidence).length > 0 && (
              <BreakdownTable title="By Confidence" data={stats.by_confidence} />
            )}
            {Object.keys(stats.by_category).length > 0 && (
              <BreakdownTable title="By Category" data={stats.by_category} />
            )}
          </div>
        </>
      )}
    </div>
  );
}
