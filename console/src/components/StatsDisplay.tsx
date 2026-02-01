interface StatsDisplayProps {
  documentCount: number;
  chunkCount: number;
}

export function StatsDisplay({ documentCount, chunkCount }: StatsDisplayProps) {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-value">{documentCount}</div>
        <div className="stat-label">Documents</div>
      </div>
      <div className="stat-card">
        <div className="stat-value">{chunkCount}</div>
        <div className="stat-label">Chunks</div>
      </div>
      <div className="stat-card">
        <div className="stat-value">
          {documentCount > 0 ? (chunkCount / documentCount).toFixed(1) : '0'}
        </div>
        <div className="stat-label">Avg Chunks/Doc</div>
      </div>
    </div>
  );
}
