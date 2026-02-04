import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';

// Use basename from Vite's base config (set at build time)
// For Render: '/', for GitHub Pages: '/FlightsKB/'
// In dev mode, always use '/' regardless of BASE_URL
const basename = import.meta.env.DEV ? '/' : import.meta.env.BASE_URL;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={basename}>
      <App />
    </BrowserRouter>
  </StrictMode>
);
