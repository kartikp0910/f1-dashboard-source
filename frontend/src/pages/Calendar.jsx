import { useCallback } from 'react';
import { fetchJson, formatDateTime, getRaceStatus, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Calendar({ apiBase = 'http://localhost:8000' }) {
  const fetchRaces = useCallback(() => fetchJson(`${apiBase}/races?season=current`), [apiBase]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchRaces, [apiBase], {
    intervalMs: 90000,
  });
  const races = data || [];

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading race calendar...</div>;
  }

  return (
    <div className="page calendar-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Race schedule</span>
          <h1>Current season calendar</h1>
        </div>
        <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="live-strip">
        <span className="live-pill">Live schedule</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'No refresh yet'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <div className="race-timeline">
        {races.map((race, index) => {
          const status = getRaceStatus(race);
          return (
            <article key={`${race.season}-${race.round}`} className={`race-card ${status.toLowerCase().replace(' ', '-')}`} style={{ '--delay': `${index * 35}ms` }}>
              <div className="timeline-node" />
              <div className="race-header">
                <span className="round">Round {race.round}</span>
                <span className="status-chip">{status}</span>
              </div>
              <h3>{race.race_name}</h3>
              <p className="circuit">{race.circuit_name}</p>
              <p className="date">{formatDateTime(race.date, race.time)}</p>
              <div className="race-actions">
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => { window.location.hash = `predict`; }}
                >
                  Predict
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => { window.location.hash = `race-detail/id=${race.race_id}`; }}
                >
                  Details
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
