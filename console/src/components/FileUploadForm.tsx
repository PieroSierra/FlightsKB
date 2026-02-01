import { useState, useRef, useEffect } from 'react';
import type { IngestMetadata, SourceKind, ConfidenceLevel } from '../types';

interface FileUploadFormProps {
  onSubmit: (file: File, contentType: 'txt' | 'pdf' | 'html', metadata: IngestMetadata) => void;
  isLoading: boolean;
  categories: string[];
  defaultCategory: string;
}

const ACCEPTED_TYPES: Record<string, 'txt' | 'pdf' | 'html'> = {
  'text/plain': 'txt',
  'application/pdf': 'pdf',
  'text/html': 'html',
};

const ACCEPTED_EXTENSIONS = ['.txt', '.pdf', '.html', '.htm'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

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

export function FileUploadForm({ onSubmit, isLoading, categories, defaultCategory }: FileUploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState(defaultCategory);
  const [kind, setKind] = useState<SourceKind>('internal');
  const [confidence, setConfidence] = useState<ConfidenceLevel>('medium');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-generate title from filename
  useEffect(() => {
    if (file && !title) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setTitle(nameWithoutExt.slice(0, 60));
    }
  }, [file, title]);

  const getContentType = (file: File): 'txt' | 'pdf' | 'html' | null => {
    // Check by MIME type first
    if (ACCEPTED_TYPES[file.type]) {
      return ACCEPTED_TYPES[file.type];
    }

    // Fall back to extension
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (ext === '.txt') return 'txt';
    if (ext === '.pdf') return 'pdf';
    if (ext === '.html' || ext === '.htm') return 'html';

    return null;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setError(null);
    setTitle('');

    if (!selectedFile) {
      setFile(null);
      return;
    }

    // Validate file type
    const contentType = getContentType(selectedFile);
    if (!contentType) {
      setError(`Unsupported file type. Please select a ${ACCEPTED_EXTENSIONS.join(', ')} file.`);
      setFile(null);
      return;
    }

    // Validate file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      setError(`File size exceeds ${MAX_FILE_SIZE / (1024 * 1024)}MB limit.`);
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file && !error) {
      const contentType = getContentType(file);
      if (contentType) {
        onSubmit(file, contentType, {
          title: title || undefined,
          category,
          kind,
          confidence,
        });
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label" htmlFor="file-upload">
          Select File
        </label>
        <input
          ref={fileInputRef}
          type="file"
          id="file-upload"
          accept=".txt,.pdf,.html,.htm,text/plain,application/pdf,text/html"
          onChange={handleFileChange}
          disabled={isLoading}
          style={{
            display: 'block',
            padding: '12px',
            border: '2px dashed #c2c9cd',
            borderRadius: '8px',
            width: '100%',
            cursor: 'pointer',
          }}
        />
        <p style={{ marginTop: '8px', fontSize: '0.875rem', color: '#68697f' }}>
          Accepted formats: .txt, .pdf, .html, .htm (max 5MB)
        </p>
      </div>

      {error && (
        <p style={{ color: '#f44336', marginBottom: '16px' }}>
          {error}
        </p>
      )}

      {file && !error && (
        <div
          style={{
            background: '#f1f2f8',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '16px',
          }}
        >
          <p style={{ margin: 0 }}>
            <strong>Selected:</strong> {file.name} ({formatFileSize(file.size)})
          </p>
        </div>
      )}

      {file && !error && (
        <>
          <div className="form-group">
            <label className="form-label" htmlFor="file-title">
              Title
            </label>
            <input
              type="text"
              id="file-title"
              className="bpk-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Auto-generated from filename if empty"
              disabled={isLoading}
              maxLength={255}
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="file-category">
                Category
              </label>
              <select
                id="file-category"
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
              <label className="form-label" htmlFor="file-kind">
                Source Kind
              </label>
              <select
                id="file-kind"
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
              <label className="form-label" htmlFor="file-confidence">
                Confidence
              </label>
              <select
                id="file-confidence"
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
        </>
      )}

      <button type="submit" className="bpk-button" disabled={isLoading || !file || !!error}>
        {isLoading ? 'Uploading...' : 'Upload & Ingest'}
      </button>
    </form>
  );
}
