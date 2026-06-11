import { useState } from 'react';
import '../styles/layout.css';

const navItems = [
  { label: 'Overview', path: 'home', icon: 'OV' },
  { label: 'Standings', path: 'standings', icon: 'ST' },
  { label: 'Calendar', path: 'calendar', icon: 'CA' },
  { label: 'Predictions', path: 'predict', icon: 'PR' },
  { label: 'Telemetry', path: 'telemetry', icon: 'TM' },
];

export default function Layout({ children, currentPage, onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleNavClick = (path) => {
    onNavigate(path);
    setMenuOpen(false);
  };

  return (
    <div className="layout">
      <div className="track-background" aria-hidden="true" />
      <header className="header">
        <div className="header-container">
          <button className="brand" type="button" onClick={() => handleNavClick('home')}>
            <span className="brand-mark">F1</span>
            <span>
              <strong>RaceIQ</strong>
              <small>Live strategy dashboard</small>
            </span>
          </button>

          <nav className={`nav ${menuOpen ? 'open' : ''}`} aria-label="Primary navigation">
            {navItems.map((item) => (
              <button
                key={item.path}
                type="button"
                className={`nav-item ${currentPage === item.path ? 'active' : ''}`}
                onClick={() => handleNavClick(item.path)}
              >
                <span>{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>

          <button
            type="button"
            className={`menu-toggle ${menuOpen ? 'open' : ''}`}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation"
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </header>

      <main className="main-content">
        {children}
      </main>

      <footer className="footer">
        <span>Live data from Jolpica/Ergast and OpenF1-compatible telemetry endpoints.</span>
        <span className="footer-pulse">Auto-refresh enabled</span>
      </footer>
    </div>
  );
}
