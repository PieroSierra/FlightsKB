# Flights KB Console

A React-based web console for the Flights KB knowledge base, built with Skyscanner's Backpack design system.

## Features

- **Query**: Search the knowledge base using natural language
- **Ingest**: Add new content via text paste or file upload (.txt, .pdf, .html)
- **Stats**: View document and chunk counts with breakdowns
- **Admin**: Rebuild the vector index

## Prerequisites

- Node.js 18+
- Flights KB backend running (`flightskb serve`)

## Development

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The console will be available at http://localhost:5173

### Configure API URL

By default, the console connects to `http://localhost:8000`. To change this:

1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edit `VITE_API_URL` in `.env`

Or add `?api=https://your-api.com` to the URL at runtime.

## Building for Production

```bash
npm run build
```

Output is in the `dist/` directory.

## Deployment

### GitHub Pages (Automated)

Push to the `main` branch triggers automatic deployment via GitHub Actions.

The console will be available at: https://pierosierra.github.io/FlightsKB/

### Manual Deployment

```bash
npm run build
npx gh-pages -d dist
```

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Backpack** - Skyscanner design system
- **React Router** - Client-side routing

## Project Structure

```
console/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Route page components
│   ├── services/      # API client
│   └── types/         # TypeScript interfaces
├── public/            # Static assets
└── index.html         # Entry HTML
```
