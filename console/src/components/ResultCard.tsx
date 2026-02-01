import type { ChunkResult } from '../types';

interface ResultCardProps {
  result: ChunkResult;
  onClick: () => void;
}

function renderMarkdown(text: string): string {
  return text
    // Headers: ## -> h2, ### -> h3, etc.
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // Bold: **text** or __text__
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Code: `text`
    .replace(/`(.+?)`/g, '<code>$1</code>')
    // Links: [text](url)
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    // List items: - item or * item
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // Paragraphs: double newline
    .replace(/\n\n/g, '</p><p>')
    // Single newlines to <br> within paragraphs
    .replace(/\n/g, '<br>');
}

export function ResultCard({ result, onClick }: ResultCardProps) {
  const scorePercent = Math.round(result.score * 100);
  const renderedContent = renderMarkdown(result.text);

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
            flexShrink: 0,
          }}
        >
          {scorePercent}%
        </span>
      </div>
      <div
        className="chunk-content"
        dangerouslySetInnerHTML={{ __html: `<p>${renderedContent}</p>` }}
      />
      <div style={{ display: 'flex', gap: '16px', fontSize: '0.875rem', color: '#68697f', marginTop: '12px' }}>
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
