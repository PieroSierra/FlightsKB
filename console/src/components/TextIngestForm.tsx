import { useState } from 'react';

interface TextIngestFormProps {
  onSubmit: (content: string) => void;
  isLoading: boolean;
}

const MAX_TEXT_SIZE = 100 * 1024; // 100KB

export function TextIngestForm({ onSubmit, isLoading }: TextIngestFormProps) {
  const [content, setContent] = useState('');

  const byteSize = new TextEncoder().encode(content).length;
  const isOverLimit = byteSize > MAX_TEXT_SIZE;
  const sizeDisplay = byteSize > 1024 ? `${(byteSize / 1024).toFixed(1)}KB` : `${byteSize}B`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim() && !isOverLimit) {
      onSubmit(content.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label" htmlFor="ingest-text">
          Content to Ingest
        </label>
        <textarea
          id="ingest-text"
          name="ingest-text"
          className="bpk-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste your flight tips, guides, or policies here..."
          disabled={isLoading}
          style={{ minHeight: '200px', width: '100%' }}
        />
        <p
          style={{
            marginTop: '8px',
            fontSize: '0.875rem',
            color: isOverLimit ? '#f44336' : '#68697f',
          }}
        >
          {sizeDisplay} / 100KB {isOverLimit && '- Content exceeds size limit'}
        </p>
      </div>
      <button type="submit" className="bpk-button" disabled={isLoading || !content.trim() || isOverLimit}>
        {isLoading ? 'Ingesting...' : 'Ingest Content'}
      </button>
    </form>
  );
}
