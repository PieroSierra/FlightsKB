import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { QueryPage } from './pages/QueryPage';
import { IngestPage } from './pages/IngestPage';
import { StatsPage } from './pages/StatsPage';
import { AdminPage } from './pages/AdminPage';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<QueryPage />} />
        <Route path="ingest" element={<IngestPage />} />
        <Route path="stats" element={<StatsPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  );
}

export default App;
