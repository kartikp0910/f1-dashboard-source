import { useCallback, useMemo, useState } from 'react';
import { fetchJson, formatDriverName, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function DriverProfiles({ apiBase = 'http://localhost:8000' }) {
  const [query, setQuery] = useState('');
  const fetchProfiles = useCallback(() => fetchJson(`${apiBase}/drivers/profiles?season=current`), [apiBase]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchProfiles, [apiBase], {
    intervalMs: 60000,
  });
  const profiles = data || [];
  const filteredProfiles = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return profiles;
    return profiles.filter((driver) => (
      formatDriverName(driver).toLowerCase().includes(value)
      || String(driver.code || '').toLowerCase().includes(value)
      || String(driver.constructor_name || driver.team_name || '').toLowerCase().includes(value)
    ));
  }, [profiles, query]);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading driver profiles...</div>;
  }

  return (
    <div className="page profiles-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Driver room</span>
          <h1>Profiles and form</h1>
        </div>
        <div className="header-tools">
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search driver or team"
            aria-label="Search driver profiles"
          />
          <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="live-strip">
        <span className="live-pill">Profiles</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Syncing driver data'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <section className="profile-grid">
        {filteredProfiles.map((driver, index) => (
          <article
            key={driver.driver_id || driver.driver_number || `${driver.code}-${index}`}
            className="profile-card"
            style={{ '--team-color': driver.constructor_color || '#E10600', '--delay': `${index * 35}ms` }}
          >
            <div className="profile-photo">
              {driver.headshot_url ? (
                <img src={driver.headshot_url} alt={formatDriverName(driver)} />
              ) : (
                <span>{driver.code || driver.driver_number || 'F1'}</span>
              )}
            </div>
            <div className="profile-content">
              <div className="driver-header">
                <span className="driver-code">{driver.code || driver.driver_number}</span>
                <span className="driver-position">#{driver.driver_number || 'TBA'}</span>
              </div>
              <h2>{formatDriverName(driver)}</h2>
              <p>{driver.constructor_name || driver.team_name || 'Team pending'}</p>
              <div className="profile-stats">
                <div><span>Position</span><strong>P{driver.position || '-'}</strong></div>
                <div><span>Points</span><strong>{driver.points ?? '-'}</strong></div>
                <div><span>Wins</span><strong>{driver.wins ?? '-'}</strong></div>
                <div><span>Form</span><strong>{driver.form_score ?? 0}</strong></div>
              </div>
              <div className="progress-track">
                <span style={{ width: `${Math.min(100, driver.form_score || 0)}%` }} />
              </div>
            </div>
          </article>
        ))}
      </section>

      {filteredProfiles.length === 0 && (
        <div className="empty-state">
          <h2>No matching drivers</h2>
          <p>Try another driver code, surname, or constructor name.</p>
        </div>
      )}
    </div>
  );
}
