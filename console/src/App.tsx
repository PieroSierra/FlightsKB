import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { QueryPage } from './pages/QueryPage';
import { IngestPage } from './pages/IngestPage';
import { BrowsePage } from './pages/BrowsePage';
import { ConnectPage } from './pages/ConnectPage';
import { StatsPage } from './pages/StatsPage';
import { AdminPage } from './pages/AdminPage';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<QueryPage />} />
        <Route path="ingest" element={<IngestPage />} />
        <Route path="browse" element={<BrowsePage />} />
        <Route path="connect" element={<ConnectPage />} />
        <Route path="stats" element={<StatsPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
      {/* Redirect /FlightsKB/* to /* for local dev when accessing GitHub Pages URLs */}
      <Route path="/FlightsKB" element={<Navigate to="/" replace />} />
      <Route path="/FlightsKB/*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
