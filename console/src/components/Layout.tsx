import { NavLink, Outlet } from 'react-router-dom';

const BASE_URL = import.meta.env.BASE_URL;

const navItems = [
  { to: '/', label: 'Query', icon: `${BASE_URL}query.svg` },
  { to: '/ingest', label: 'Ingest', icon: `${BASE_URL}ingest.svg` },
  { to: '/browse', label: 'Browse', icon: `${BASE_URL}browse.svg` },
  { to: '/connect', label: 'Connect', icon: `${BASE_URL}connect.svg` },
  { to: '/stats', label: 'Stats', icon: `${BASE_URL}stats.svg` },
  { to: '/admin', label: 'Admin', icon: `${BASE_URL}admin.svg` },
];

const iconStyle: React.CSSProperties = {
  width: '1rem',
  height: '1rem',
  filter: 'brightness(0) invert(1)',
};

export function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-content">
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <img src={`${BASE_URL}logo.svg`} alt="" style={{ width: '1.5rem', height: '1.5rem', filter: 'brightness(0) invert(1)' }} />
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
                <img src={item.icon} alt="" style={iconStyle} />
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
