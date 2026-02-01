import { useMemo } from 'react';
import { marked } from 'marked';
import type { FileContentResponse } from '../types';

interface MarkdownViewerProps {
  content?: FileContentResponse;
  isLoading?: boolean;
  error?: string;
}

export function MarkdownViewer({ content, isLoading, error }: MarkdownViewerProps) {
  const htmlContent = useMemo(() => {
    if (!content?.content) return '';
    return marked(content.content, { async: false }) as string;
  }, [content?.content]);

  if (isLoading) {
    return (
      <div className="markdown-viewer markdown-viewer--loading">
        <div className="spinner spinner--large"></div>
        <span>Loading content...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="markdown-viewer markdown-viewer--error">
        <div className="error-banner">
          <span className="error-icon">!</span>
          <span className="error-message">{error}</span>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="markdown-viewer markdown-viewer--empty">
        <div className="empty-state">
          <p>Select a file to view its contents</p>
        </div>
      </div>
    );
  }

  const fm = content.frontmatter;
  const title = fm.title ? String(fm.title) : undefined;
  const status = fm.status ? String(fm.status) : undefined;
  const kbId = fm.kb_id ? String(fm.kb_id) : undefined;
  const type = fm.type ? String(fm.type) : undefined;
  const confidence = fm.confidence ? String(fm.confidence) : undefined;

  return (
    <div className="markdown-viewer">
      <div className="markdown-header">
        <div className="markdown-path">{content.path}</div>
        {title && <h2 className="markdown-title">{title}</h2>}
        <div className="markdown-meta">
          {status && (
            <span className={`meta-badge meta-badge--${status}`}>
              {status}
            </span>
          )}
          {kbId && (
            <span className="meta-item">
              <span className="meta-label">KB ID:</span> {kbId}
            </span>
          )}
          {type && (
            <span className="meta-item">
              <span className="meta-label">Type:</span> {type}
            </span>
          )}
          {confidence && (
            <span className="meta-item">
              <span className="meta-label">Confidence:</span> {confidence}
            </span>
          )}
        </div>
      </div>
      <div className="markdown-content">
        <div
          className="chunk-content"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      </div>
    </div>
  );
}
