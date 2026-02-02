# FlightsKB Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-01

## Active Technologies
- Python 3.11+ + ChromaDB, sentence-transformers, Click, python-frontmatter, FastAPI (optional) (001-flights-kb-playground)
- File system (Markdown in `knowledge/`) + ChromaDB (vector index) (001-flights-kb-playground)
- TypeScript 5.3+ with React 18.2+ + @skyscanner/backpack-web v41.9.0, Vite 5.0, react-router-dom 6.x (002-kb-console)
- N/A (frontend only - uses backend API) (002-kb-console)
- Python 3.11+ (backend), TypeScript 5.3+ (frontend) + FastAPI 0.100+, ChromaDB 0.4+, sentence-transformers, React 18, Vite 5 (003-render-hosting)
- GitHub API for persistence (Markdown files), ChromaDB for vector index (ephemeral/rebuildable) (003-render-hosting)

- (001-flights-kb-playground)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

# Add commands for 

## Code Style

: Follow standard conventions

## Recent Changes
- 003-render-hosting: Added Python 3.11+ (backend), TypeScript 5.3+ (frontend) + FastAPI 0.100+, ChromaDB 0.4+, sentence-transformers, React 18, Vite 5
- 002-kb-console: Added TypeScript 5.3+ with React 18.2+ + @skyscanner/backpack-web v41.9.0, Vite 5.0, react-router-dom 6.x
- 001-flights-kb-playground: Added Python 3.11+ + ChromaDB, sentence-transformers, Click, python-frontmatter, FastAPI (optional)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
