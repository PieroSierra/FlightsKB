# KB Console - Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Flights KB backend running (`flightskb serve`)
- Git repository cloned

## Local Development

### 1. Install Dependencies

```bash
cd console
npm install
```

### 2. Start Backend API

In a separate terminal:
```bash
cd /path/to/FlightsKB
source .venv/bin/activate
flightskb serve --port 8000
```

### 3. Start Frontend Development Server

```bash
cd console
npm run dev
```

Open http://localhost:5173 in your browser.

## Configuration

### API URL

By default, the console connects to `http://localhost:8000`.

To change the API URL:
- Set `VITE_API_URL` environment variable before building
- Or add `?api=https://your-api.com` to the URL

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

## Building for Production

```bash
npm run build
```

Output is in `dist/` folder, ready for static hosting.

## Deploying to GitHub Pages

### Manual Deployment

```bash
npm run build
npx gh-pages -d dist
```

### Automated (GitHub Actions)

Push to `main` branch triggers automatic deployment via `.github/workflows/deploy-console.yml`.

## Using the Console

### Query Page (Home)

1. Enter search text in the query field
2. Adjust K value (number of results) using the dropdown
3. Click "Search" or press Enter
4. View results as cards showing chunk text and similarity score
5. Click a result card to see full metadata

### Ingest Page

**Text Input:**
1. Select "Text" tab
2. Paste content into the text area
3. Click "Ingest"
4. View confirmation with generated KB ID

**File Upload:**
1. Select "File" tab
2. Click "Choose File" and select .txt, .pdf, or .html
3. Click "Ingest"
4. View confirmation with generated KB ID

### Stats Page

Displays:
- Total documents and chunks
- Breakdown by type, status, and confidence
- Index health information

### Admin Page

- **Rebuild Index**: Click to trigger full re-indexing
- Shows progress during rebuild
- Displays summary on completion

## Troubleshooting

### "Connection Error" on page load

- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS is enabled in backend
- Verify API URL is correct

### Query returns no results

- Run `flightskb stats` to verify index has documents
- Try broader search terms
- Run `flightskb rebuild` to refresh index

### Ingest fails with "Parse Failed"

- Verify file is valid (not corrupted)
- Check file size is under 5MB
- For PDFs, ensure they contain extractable text (not scanned images)

## Architecture

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────┐
│   KB Console    │ ◄──────────────────► │   FastAPI        │
│   (React/Vite)  │                      │   Backend        │
│                 │                      │                  │
│  GitHub Pages   │                      │  Railway/Render  │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                         ┌────────▼─────────┐
                                         │   ChromaDB       │
                                         │   + Knowledge/   │
                                         └──────────────────┘
```
