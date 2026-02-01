import { useState, useRef } from 'react';

interface FileUploadFormProps {
  onSubmit: (file: File, contentType: 'txt' | 'pdf' | 'html') => void;
  isLoading: boolean;
}

const ACCEPTED_TYPES: Record<string, 'txt' | 'pdf' | 'html'> = {
  'text/plain': 'txt',
  'application/pdf': 'pdf',
  'text/html': 'html',
};

const ACCEPTED_EXTENSIONS = ['.txt', '.pdf', '.html', '.htm'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export function FileUploadForm({ onSubmit, isLoading }: FileUploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
        onSubmit(file, contentType);
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

      <button type="submit" className="bpk-button" disabled={isLoading || !file || !!error}>
        {isLoading ? 'Uploading...' : 'Upload & Ingest'}
      </button>
    </form>
  );
}
