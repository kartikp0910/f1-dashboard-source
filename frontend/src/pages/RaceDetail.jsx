import { useCallback } from 'react';
import { fetchJson, formatDateTime, getRaceStatus, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function RaceDetail({ raceId, apiBase = 'http://localhost:8000' }) {
  const fetchRaces = useCallback(() => fetchJson(`${apiBase}/races?season=current`), [apiBase]);
  const { data, loading, error } = useLiveResource(fetchRaces, [apiBase], { intervalMs: 90000 });
  const races = data || [];
  const race = races.find((item) => item.race_id === raceId);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading race details...</div>;
  }

  return (
    <div className="page race-detail-page">
      <button type="button" onClick={() => { window.location.hash = 'calendar'; }} className="text-button">
        Back to calendar
      </button>

      {error && <div className="error-message">{error}</div>}

      {race ? (
        <section className="race-detail-panel">
          <span className="eyebrow">{getRaceStatus(race)}</span>
          <h1>{race.race_name}</h1>
          <div className="dashboard-grid">
            <article className="insight-panel">
              <span className="panel-label">Circuit</span>
              <h2>{race.circuit_name}</h2>
              <p>{race.circuit_id}</p>
            </article>
            <article className="insight-panel">
              <span className="panel-label">Round</span>
              <h2>{race.round}</h2>
              <p>{race.season} season</p>
            </article>
            <article className="insight-panel">
              <span className="panel-label">Session date</span>
              <h2>{formatDateTime(race.date, race.time)}</h2>
              <p>Local display time</p>
            </article>
          </div>
          <button type="button" className="btn btn-primary" onClick={() => { window.location.hash = 'predict'; }}>
            Use in prediction model
          </button>
        </section>
      ) : (
        <div className="info-message">Race details are not available for this round.</div>
      )}
    </div>
  );
}
