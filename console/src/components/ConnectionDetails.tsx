import { useState } from 'react';
import { API_URL } from '../services/api';

export function ConnectionDetails() {
  const [copied, setCopied] = useState<string>();

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
      setTimeout(() => setCopied(undefined), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(id);
      setTimeout(() => setCopied(undefined), 2000);
    }
  };

  const curlQuery = `curl -X POST "${API_URL}/api/query" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "your search query", "k": 5}'`;

  const curlHealth = `curl "${API_URL}/api/health"`;

  const curlStats = `curl "${API_URL}/api/stats"`;

  return (
    <div className="connection-details">
      <div className="connection-section">
        <h3>API Base URL</h3>
        <div className="code-block">
          <code>{API_URL}</code>
          <button
            className="copy-button"
            onClick={() => copyToClipboard(API_URL, 'url')}
          >
            {copied === 'url' ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div className="connection-section">
        <h3>Health Check</h3>
        <p className="section-description">Check if the API is running:</p>
        <div className="code-block">
          <pre>{curlHealth}</pre>
          <button
            className="copy-button"
            onClick={() => copyToClipboard(curlHealth, 'health')}
          >
            {copied === 'health' ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div className="connection-section">
        <h3>Query Endpoint</h3>
        <p className="section-description">Search the knowledge base:</p>
        <div className="code-block">
          <pre>{curlQuery}</pre>
          <button
            className="copy-button"
            onClick={() => copyToClipboard(curlQuery, 'query')}
          >
            {copied === 'query' ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div className="connection-section">
        <h3>Stats Endpoint</h3>
        <p className="section-description">Get knowledge base statistics:</p>
        <div className="code-block">
          <pre>{curlStats}</pre>
          <button
            className="copy-button"
            onClick={() => copyToClipboard(curlStats, 'stats')}
          >
            {copied === 'stats' ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div className="connection-section">
        <h3>Available Endpoints</h3>
        <table className="endpoints-table">
          <thead>
            <tr>
              <th>Method</th>
              <th>Endpoint</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>GET</code></td>
              <td><code>/api/health</code></td>
              <td>Health check</td>
            </tr>
            <tr>
              <td><code>POST</code></td>
              <td><code>/api/query</code></td>
              <td>Search the knowledge base</td>
            </tr>
            <tr>
              <td><code>GET</code></td>
              <td><code>/api/stats</code></td>
              <td>Get index statistics</td>
            </tr>
            <tr>
              <td><code>GET</code></td>
              <td><code>/api/categories</code></td>
              <td>List available categories</td>
            </tr>
            <tr>
              <td><code>POST</code></td>
              <td><code>/api/ingest</code></td>
              <td>Ingest new content (requires API key)</td>
            </tr>
            <tr>
              <td><code>POST</code></td>
              <td><code>/api/rebuild</code></td>
              <td>Rebuild the index (requires API key)</td>
            </tr>
            <tr>
              <td><code>GET</code></td>
              <td><code>/api/files/tree</code></td>
              <td>Get file tree structure</td>
            </tr>
            <tr>
              <td><code>GET</code></td>
              <td><code>/api/files/content</code></td>
              <td>Get file content</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
