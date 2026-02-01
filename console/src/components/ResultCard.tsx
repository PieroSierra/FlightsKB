import type { ChunkResult } from '../types';

interface ResultCardProps {
  result: ChunkResult;
  onClick: () => void;
}

export function ResultCard({ result, onClick }: ResultCardProps) {
  const scorePercent = Math.round(result.score * 100);

  return (
    <div className="card result-card" onClick={onClick} style={{ cursor: 'pointer' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
          {result.title}
        </h3>
        <span
          style={{
            backgroundColor: scorePercent >= 70 ? '#4caf50' : scorePercent >= 40 ? '#ff9800' : '#f44336',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.875rem',
            fontWeight: 600,
          }}
        >
          {scorePercent}%
        </span>
      </div>
      <p style={{ margin: '0 0 12px 0', color: '#444' }}>
        {result.text.length > 200 ? `${result.text.slice(0, 200)}...` : result.text}
      </p>
      <div style={{ display: 'flex', gap: '16px', fontSize: '0.875rem', color: '#68697f' }}>
        <span>
          <strong>ID:</strong> {result.kb_id}
        </span>
        {result.metadata.confidence && (
          <span>
            <strong>Confidence:</strong> {result.metadata.confidence}
          </span>
        )}
        {result.metadata.type && (
          <span>
            <strong>Type:</strong> {result.metadata.type}
          </span>
        )}
      </div>
    </div>
  );
}
