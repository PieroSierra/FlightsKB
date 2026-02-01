import type { RebuildResponse } from '../types';

interface RebuildSummaryProps {
  result: RebuildResponse;
}

export function RebuildSummary({ result }: RebuildSummaryProps) {
  return (
    <div className="success-message">
      <h3 style={{ color: '#2e7d32', margin: '0 0 16px 0' }}>
        Index Rebuilt Successfully
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
        <div>
          <p style={{ margin: 0, color: '#68697f', fontSize: '0.875rem' }}>
            Documents Processed
          </p>
          <p style={{ margin: '4px 0 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
            {result.documents_processed}
          </p>
        </div>
        <div>
          <p style={{ margin: 0, color: '#68697f', fontSize: '0.875rem' }}>
            Chunks Indexed
          </p>
          <p style={{ margin: '4px 0 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
            {result.chunks_indexed}
          </p>
        </div>
        <div>
          <p style={{ margin: 0, color: '#68697f', fontSize: '0.875rem' }}>
            Duration
          </p>
          <p style={{ margin: '4px 0 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
            {result.duration_seconds.toFixed(2)}s
          </p>
        </div>
      </div>
      {result.errors.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <p style={{ color: '#f44336', marginBottom: '8px' }}>
            Warnings ({result.errors.length}):
          </p>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {result.errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
