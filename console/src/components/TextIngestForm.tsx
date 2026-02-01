import { useState, useEffect } from 'react';
import type { IngestMetadata, SourceKind, ConfidenceLevel } from '../types';

interface TextIngestFormProps {
  onSubmit: (content: string, metadata: IngestMetadata) => void;
  isLoading: boolean;
  categories: string[];
  defaultCategory: string;
}

const MAX_TEXT_SIZE = 100 * 1024; // 100KB

const KIND_OPTIONS: { value: SourceKind; label: string }[] = [
  { value: 'internal', label: 'Internal' },
  { value: 'ugc', label: 'User Generated' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'press', label: 'Press' },
  { value: 'blog', label: 'Blog' },
  { value: 'forum', label: 'Forum' },
  { value: 'other', label: 'Other' },
];

const CONFIDENCE_OPTIONS: { value: ConfidenceLevel; label: string }[] = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

export function TextIngestForm({ onSubmit, isLoading, categories, defaultCategory }: TextIngestFormProps) {
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState(defaultCategory);
  const [kind, setKind] = useState<SourceKind>('internal');
  const [confidence, setConfidence] = useState<ConfidenceLevel>('medium');

  // Auto-generate title from content
  useEffect(() => {
    if (!title && content) {
      const firstLine = content.split('\n')[0].trim();
      setTitle(firstLine.slice(0, 60));
    }
  }, [content, title]);

  const byteSize = new TextEncoder().encode(content).length;
  const isOverLimit = byteSize > MAX_TEXT_SIZE;
  const sizeDisplay = byteSize > 1024 ? `${(byteSize / 1024).toFixed(1)}KB` : `${byteSize}B`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim() && !isOverLimit) {
      onSubmit(content.trim(), {
        title: title || undefined,
        category,
        kind,
        confidence,
      });
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

      <div className="form-group">
        <label className="form-label" htmlFor="ingest-title">
          Title
        </label>
        <input
          type="text"
          id="ingest-title"
          className="bpk-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Auto-generated from content if empty"
          disabled={isLoading}
          maxLength={255}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '16px' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="ingest-category">
            Category
          </label>
          <select
            id="ingest-category"
            className="bpk-select"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            disabled={isLoading}
            style={{ width: '100%' }}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="ingest-kind">
            Source Kind
          </label>
          <select
            id="ingest-kind"
            className="bpk-select"
            value={kind}
            onChange={(e) => setKind(e.target.value as SourceKind)}
            disabled={isLoading}
            style={{ width: '100%' }}
          >
            {KIND_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="ingest-confidence">
            Confidence
          </label>
          <select
            id="ingest-confidence"
            className="bpk-select"
            value={confidence}
            onChange={(e) => setConfidence(e.target.value as ConfidenceLevel)}
            disabled={isLoading}
            style={{ width: '100%' }}
          >
            {CONFIDENCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button type="submit" className="bpk-button" disabled={isLoading || !content.trim() || isOverLimit}>
        {isLoading ? 'Ingesting...' : 'Ingest Content'}
      </button>
    </form>
  );
}
