import { useCallback } from 'react';
import { fetchJson, formatDateTime, formatDriverName, getNextRace, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Home({ apiBase = 'http://localhost:8000' }) {
  const fetchOverview = useCallback(async () => {
    const [standingsResult, racesResult] = await Promise.allSettled([
      fetchJson(`${apiBase}/standings?season=current`),
      fetchJson(`${apiBase}/races?season=current`),
    ]);
    const standings = standingsResult.status === 'fulfilled' ? standingsResult.value : [];
    const races = racesResult.status === 'fulfilled' ? racesResult.value : [];
    if (!standings.length && !races.length) {
      throw new Error('Live F1 providers are temporarily unavailable');
    }
    return { standings, races };
  }, [apiBase]);

  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchOverview, [apiBase], {
    intervalMs: 45000,
  });

  const standings = data?.standings || [];
  const races = data?.races || [];
  const nextRace = getNextRace(races);
  const leader = standings[0];
  const totalWins = standings.reduce((sum, driver) => sum + Number(driver.wins || 0), 0);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading live race control...</div>;
  }

  return (
    <div className="page home-page">
      <section className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">Live F1 command center</span>
          <h1>Championship data, predictive race intelligence, and telemetry in one cockpit.</h1>
          <p>
            Current standings, upcoming rounds, prediction inputs, and session telemetry refresh automatically from live API sources.
          </p>
          <div className="hero-actions">
            <button type="button" className="btn btn-primary" onClick={() => { window.location.hash = 'predict'; }}>Run prediction</button>
            <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
              {refreshing ? 'Refreshing...' : 'Refresh live data'}
            </button>
          </div>
        </div>
        <div className="race-orbit" aria-hidden="true">
          <div className="orbit-line" />
          <div className="car-dot" />
          <div className="sector sector-one" />
          <div className="sector sector-two" />
          <div className="sector sector-three" />
        </div>
      </section>

      <div className="live-strip">
        <span className="live-pill">Live</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Waiting for first update'}</span>
        {error && <span className="muted">Data source warning: {error}</span>}
      </div>

      <section className="dashboard-grid">
        <article className="insight-panel primary">
          <span className="panel-label">Championship leader</span>
          <h2>{formatDriverName(leader)}</h2>
          <p>{leader?.constructor_name || 'Team pending'}</p>
          <div className="metric-row">
            <span>{leader?.points ?? 0}<small>points</small></span>
            <span>{leader?.wins ?? 0}<small>wins</small></span>
          </div>
        </article>

        <article className="insight-panel">
          <span className="panel-label">Next race</span>
          <h2>{nextRace?.race_name || 'Calendar pending'}</h2>
          <p>{nextRace?.circuit_name || 'Awaiting schedule'}</p>
          <strong>{nextRace ? formatDateTime(nextRace.date, nextRace.time) : 'TBA'}</strong>
        </article>

        <article className="insight-panel">
          <span className="panel-label">Season pulse</span>
          <h2>{races.length}</h2>
          <p>Races tracked this season</p>
          <strong>{totalWins} wins recorded</strong>
        </article>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Driver form</span>
            <h2>Top five live standings</h2>
          </div>
          <button type="button" className="text-button" onClick={() => { window.location.hash = 'standings'; }}>View all</button>
        </div>
        <div className="driver-grid">
          {standings.slice(0, 5).map((driver, index) => (
            <article
              key={driver.driver_id}
              className="driver-card"
              style={{ '--team-color': driver.constructor_color || '#e10600', '--delay': `${index * 70}ms` }}
            >
              <div className="driver-header">
                <span className="driver-code">{driver.code}</span>
                <span className="driver-position">P{driver.position}</span>
              </div>
              <h3>{formatDriverName(driver)}</h3>
              <p className="driver-team">{driver.constructor_name}</p>
              <div className="progress-track">
                <span style={{ width: `${Math.min(100, (Number(driver.points || 0) / Math.max(Number(leader?.points || 1), 1)) * 100)}%` }} />
              </div>
              <div className="driver-stats">
                <div className="stat">
                  <span className="stat-label">Points</span>
                  <span className="stat-value">{driver.points}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Wins</span>
                  <span className="stat-value">{driver.wins}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
        {standings.length === 0 && (
          <div className="empty-state">
            <h2>Live standings are unavailable</h2>
            <p>{error || 'The data provider returned no championship entries.'}</p>
          </div>
        )}
      </section>
    </div>
  );
}
