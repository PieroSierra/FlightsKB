import { ConnectionDetails } from '../components/ConnectionDetails';

export function ConnectPage() {
  return (
    <div className="connect-page">
      <header className="page-header">
        <h2 className="page-title">Connect to Knowledge Base</h2>
        <p className="page-description">
          API documentation and connection details for integrating with the Flights KB.
        </p>
      </header>

      <div className="card">
        <h3>About Flights KB</h3>
        <p>
          Flights KB is a knowledge base system that stores flight-related information
          in Markdown files with semantic search capabilities. It uses vector embeddings
          to enable natural language search across all indexed content.
        </p>
        <p>
          Content is organized into categories (airlines, hacks, lounges, etc.) and can
          be searched using the Query API or browsed through this console.
        </p>
      </div>

      <div className="card">
        <h3>Key Features</h3>
        <ul className="feature-list">
          <li>
            <strong>Semantic Search</strong> - Find relevant content using natural language queries
          </li>
          <li>
            <strong>Markdown Storage</strong> - All knowledge stored as plain Markdown files with YAML frontmatter
          </li>
          <li>
            <strong>Multi-source Ingestion</strong> - Import content from text, PDFs, HTML, and more
          </li>
          <li>
            <strong>Category Organization</strong> - Content organized by category for easy browsing
          </li>
          <li>
            <strong>Confidence Levels</strong> - Track reliability of information sources
          </li>
        </ul>
      </div>

      <div className="card">
        <ConnectionDetails />
      </div>
    </div>
  );
}
