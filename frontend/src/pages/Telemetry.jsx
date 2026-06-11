import { useCallback, useState } from 'react';
import { fetchJson, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Telemetry({ apiBase = 'http://localhost:8000' }) {
  const [driverId, setDriverId] = useState('latest');
  const fetchTelemetry = useCallback(() => fetchJson(`${apiBase}/telemetry?race_id=latest&driver_id=${driverId}`), [apiBase, driverId]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchTelemetry, [apiBase, driverId], {
    intervalMs: 12000,
  });
  const telemetry = data || [];

  if (loading) {
    return <div className="loading"><span className="spinner" />Connecting to live telemetry...</div>;
  }

  return (
    <div className="page telemetry-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Open session stream</span>
          <h1>Telemetry board</h1>
        </div>
        <div className="header-tools">
          <select value={driverId} onChange={(e) => setDriverId(e.target.value)} aria-label="Select telemetry driver">
            <option value="latest">Fastest available drivers</option>
            <option value="1">Driver 1</option>
            <option value="4">Driver 4</option>
            <option value="16">Driver 16</option>
            <option value="44">Driver 44</option>
            <option value="63">Driver 63</option>
          </select>
          <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="live-strip">
        <span className="live-pill">Live telemetry</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'No packets yet'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <div className="telemetry-grid">
        {telemetry.map((data, index) => (
          <article key={`${data.driver_id}-${index}`} className="telemetry-card" style={{ '--delay': `${index * 70}ms` }}>
            <div className="telemetry-card-header">
              <div>
                <span className="driver-code">{data.driver_id}</span>
                <h3>{data.driver_name}</h3>
              </div>
              <span className={`drs-pill ${data.drs ? 'active' : ''}`}>DRS {data.drs ? 'on' : 'off'}</span>
            </div>

            <div className="speedometer" style={{ '--speed': `${Math.min(100, (data.speed / 360) * 100)}%` }}>
              <strong>{Math.round(data.speed)}</strong>
              <span>km/h</span>
            </div>

            <div className="telemetry-bars">
              <div className="metric">
                <label>Throttle</label>
                <div className="progress-track"><span style={{ width: `${data.throttle * 100}%` }} /></div>
                <strong>{Math.round(data.throttle * 100)}%</strong>
              </div>
              <div className="metric">
                <label>Brake</label>
                <div className="progress-track brake"><span style={{ width: `${data.brake * 100}%` }} /></div>
                <strong>{Math.round(data.brake * 100)}%</strong>
              </div>
              <div className="metric compact-metric">
                <label>Gear</label>
                <strong>{data.gear}</strong>
              </div>
              <div className="metric compact-metric">
                <label>Lap</label>
                <strong>{data.lap}</strong>
              </div>
            </div>
          </article>
        ))}
      </div>
      {!loading && telemetry.length === 0 && (
        <div className="empty-state">
          <h2>No telemetry packets available</h2>
          <p>{error || 'The latest session has no recent car data. Try again during or shortly after an F1 session.'}</p>
        </div>
      )}
    </div>
  );
}
