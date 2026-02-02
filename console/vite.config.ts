import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  // Use '/' for Render deployment (default), '/FlightsKB/' for GitHub Pages
  base: mode === 'ghpages' ? '/FlightsKB/' : '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    proxy: {
      // Proxy /api requests to FastAPI backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite needed - backend now serves at /api prefix
      },
    },
  },
}))
