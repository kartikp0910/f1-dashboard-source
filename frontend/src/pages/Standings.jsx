import { useCallback, useState } from 'react';
import { fetchJson, formatDriverName, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Standings({ apiBase = 'http://localhost:8000' }) {
  const [season, setSeason] = useState('current');
  const fetchStandings = useCallback(() => fetchJson(`${apiBase}/standings?season=${season}`), [apiBase, season]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchStandings, [season, apiBase], {
    intervalMs: season === 'current' ? 45000 : 0,
  });
  const standings = data || [];

  const leaderPoints = Number(standings?.[0]?.points || 1);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading championship order...</div>;
  }

  return (
    <div className="page standings-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Live championship table</span>
          <h1>Driver standings</h1>
        </div>
        <div className="header-tools">
          <select value={season} onChange={(e) => setSeason(e.target.value)} aria-label="Select season">
            <option value="current">Current season</option>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
          </select>
          <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="live-strip">
        <span className="live-pill">{season === 'current' ? 'Live' : 'Archive'}</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'No refresh yet'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <div className="standings-stack">
        {standings.map((driver, index) => (
          <article
            key={driver.driver_id}
            className="standing-row"
            style={{ '--team-color': driver.constructor_color || '#e10600', '--delay': `${index * 35}ms` }}
          >
            <div className="rank">#{driver.position}</div>
            <div className="driver-identity">
              <span className="driver-code">{driver.code}</span>
              <div>
                <h3>{formatDriverName(driver)}</h3>
                <p>{driver.constructor_name}</p>
              </div>
            </div>
            <div className="standing-bar" aria-hidden="true">
              <span style={{ width: `${Math.max(4, (Number(driver.points || 0) / leaderPoints) * 100)}%` }} />
            </div>
            <div className="standing-stats">
              <strong>{driver.points}</strong>
              <span>pts</span>
            </div>
            <div className="standing-stats">
              <strong>{driver.wins}</strong>
              <span>wins</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
