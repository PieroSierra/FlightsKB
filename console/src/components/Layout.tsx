import { NavLink, Outlet } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Query' },
  { to: '/ingest', label: 'Ingest' },
  { to: '/stats', label: 'Stats' },
  { to: '/admin', label: 'Admin' },
];

export function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-content">
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
            Flights KB Console
          </h1>
          <nav className="app-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'nav-link--active' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
