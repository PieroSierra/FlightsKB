import { useState, useEffect } from 'react';
import { TextIngestForm } from '../components/TextIngestForm';
import { FileUploadForm } from '../components/FileUploadForm';
import { ErrorBanner } from '../components/ErrorBanner';
import { api } from '../services/api';
import type { IngestResponse, ApiError, IngestMetadata } from '../types';

type TabMode = 'text' | 'file';

export function IngestPage() {
  const [mode, setMode] = useState<TabMode>('text');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [defaultCategory, setDefaultCategory] = useState('');
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);

  // Fetch categories on mount
  useEffect(() => {
    setCategoriesLoading(true);
    setCategoriesError(null);
    api.getCategories()
      .then((response) => {
        setCategories(response.categories);
        setDefaultCategory(response.default);
      })
      .catch((err) => {
        console.error('Failed to fetch categories:', err);
        setCategoriesError('Failed to load categories. Is the backend running?');
        setCategories([]);
        setDefaultCategory('');
      })
      .finally(() => {
        setCategoriesLoading(false);
      });
  }, []);

  const handleTextIngest = async (content: string, metadata: IngestMetadata) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.ingest({
        content_type: 'text',
        content,
        title: metadata.title,
        category: metadata.category,
        kind: metadata.kind,
        confidence: metadata.confidence,
      });
      setResult(response);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to ingest content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileIngest = async (file: File, contentType: 'txt' | 'pdf' | 'html', metadata: IngestMetadata) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Read file as base64
      const content = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64 = (reader.result as string).split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const response = await api.ingest({
        content_type: contentType,
        content,
        filename: file.name,
        title: metadata.title,
        category: metadata.category,
        kind: metadata.kind,
        confidence: metadata.confidence,
      });
      setResult(response);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to upload file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleIngestAnother = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Ingest Content</h2>
        <p className="page-description">
          Add new knowledge to the database by pasting text or uploading files.
        </p>
      </div>

      {result && (
        <div className="success-message">
          <h3>Content Ingested Successfully!</h3>
          <p>
            <strong>KB ID:</strong> {result.kb_id}
          </p>
          <p>
            <strong>File Path:</strong> {result.file_path}
          </p>
          <p>
            <strong>Title:</strong> {result.title}
          </p>
          <p>
            <strong>Chunks Created:</strong> {result.chunk_count}
          </p>
          <button
            onClick={handleIngestAnother}
            className="bpk-button"
            style={{ marginTop: '12px' }}
          >
            Ingest Another
          </button>
        </div>
      )}

      {error && (
        <div style={{ marginBottom: '16px' }}>
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {categoriesError && (
        <div style={{ marginBottom: '16px' }}>
          <ErrorBanner message={categoriesError} onDismiss={() => setCategoriesError(null)} />
        </div>
      )}

      {!result && (
        <>
          <div className="tabs">
            <button
              className={`tab-button ${mode === 'text' ? 'tab-button--active' : ''}`}
              onClick={() => setMode('text')}
              type="button"
            >
              Paste Text
            </button>
            <button
              className={`tab-button ${mode === 'file' ? 'tab-button--active' : ''}`}
              onClick={() => setMode('file')}
              type="button"
            >
              Upload File
            </button>
          </div>

          <div className="card">
            {categoriesLoading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Loading categories...
              </div>
            ) : mode === 'text' ? (
              <TextIngestForm
                onSubmit={handleTextIngest}
                isLoading={isLoading}
                categories={categories}
                defaultCategory={defaultCategory}
              />
            ) : (
              <FileUploadForm
                onSubmit={handleFileIngest}
                isLoading={isLoading}
                categories={categories}
                defaultCategory={defaultCategory}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
