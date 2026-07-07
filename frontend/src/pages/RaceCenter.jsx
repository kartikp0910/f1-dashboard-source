import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchJson, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

function formatDelta(value) {
  if (value === null || value === undefined || value === '') return 'Leader';
  if (typeof value === 'string') return value;
  return `+${Number(value).toFixed(3)}s`;
}

function formatWeather(value, suffix = '') {
  if (value === null || value === undefined) return 'N/A';
  return `${Number(value).toFixed(1)}${suffix}`;
}

function formatCountdown(ms) {
  if (!Number.isFinite(ms) || ms <= 0) return '00d 00h 00m 00s';
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${String(days).padStart(2, '0')}d ${String(hours).padStart(2, '0')}h ${String(minutes).padStart(2, '0')}m ${String(seconds).padStart(2, '0')}s`;
}

function isLiveRaceSession(trackData) {
  if (trackData?.is_live === false) return false;
  if (trackData?.mode === 'fastf1-live') return true;
  const session = trackData.session || {};
  const type = `${session.session_type || ''} ${session.session_name || ''}`.toLowerCase();
  if (!type.includes('race')) return false;

  const now = Date.now();
  const startsAt = session.date_start ? new Date(session.date_start).getTime() : null;
  const endsAt = session.date_end ? new Date(session.date_end).getTime() : null;
  if (Number.isFinite(startsAt) && Number.isFinite(endsAt)) {
    return now >= startsAt && now <= endsAt + 30 * 60 * 1000;
  }
  if (Number.isFinite(startsAt)) {
    return now >= startsAt && now <= startsAt + 4 * 60 * 60 * 1000;
  }
  return false;
}

export default function RaceCenter({ apiBase = 'http://localhost:8000' }) {
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [now, setNow] = useState(() => Date.now());
  const fetchRaceCenter = useCallback(() => fetchJson(`${apiBase}/live/track`), [apiBase]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchRaceCenter, [apiBase], {
    intervalMs: 4000,
  });

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const trackData = data || {};
  const raceSummary = trackData?.race_state || {};
  const cars = trackData?.cars || [];
  const activeDriver = useMemo(
    () => cars.find((car) => car.driver_number === selectedDriver) || cars[0],
    [cars, selectedDriver],
  );
  const session = trackData?.session || {};
  const weather = trackData?.weather || {};
  const raceControl = trackData?.race_control || [];
  const liveRace = isLiveRaceSession(trackData);
  const nextRaceStartsAt = raceSummary?.next_race?.starts_at ? new Date(raceSummary.next_race.starts_at).getTime() : null;
  const countdown = formatCountdown((nextRaceStartsAt || now) - now);

  if (loading) {
    return <div className="loading"><span className="spinner" />Opening live race center...</div>;
  }

  return (
    <div className="page race-center-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Continuous live map</span>
          <h1>Race center</h1>
          <p>{session.circuit_short_name || session.location || 'Latest OpenF1 session'} - {session.session_name || 'Session'}</p>
        </div>
        <div className="header-tools">
          <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
            {refreshing ? 'Syncing...' : 'Force sync'}
          </button>
        </div>
      </div>

      <div className="live-strip">
        <span className={`live-pill ${liveRace ? '' : 'demo'}`}>{liveRace ? 'Live race' : 'No live race'}</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Waiting for packets'}</span>
        <span>Refresh target {trackData?.refresh_ms || 4000}ms</span>
        {(error || trackData?.provider_warning) && <span className="muted">{error || trackData.provider_warning}</span>}
      </div>

      {!liveRace && (
        <>
          <section className="no-race-panel">
            <div>
              <span className="eyebrow">No current race happening</span>
              <h2>uh oh you are early by</h2>
              <strong className="countdown-clock">{countdown}</strong>
              <p>
                Next up: {raceSummary?.next_race?.race_name || 'Next race'} at {raceSummary?.next_race?.circuit_name || 'TBA'}.
              </p>
            </div>
            <div className="next-race-card">
              <span>Next race</span>
              <strong>{raceSummary?.next_race?.race_name || 'TBA'}</strong>
              <p>{raceSummary?.next_race?.starts_at ? new Date(raceSummary.next_race.starts_at).toLocaleString() : 'Schedule pending'}</p>
            </div>
          </section>
        </>
      )}

      {liveRace && <section className="race-control-grid">
        <article className="track-stage">
          <div className="track-map" aria-label="Live driver track positions">
            <svg className="circuit-svg" viewBox="0 0 100 100" role="img" aria-label="Stylized race circuit">
              <path
                d="M18 58 C 11 38, 23 15, 45 16 C 72 17, 88 28, 85 48 C 82 70, 65 85, 42 80 C 23 76, 22 65, 34 58 C 48 50, 62 57, 67 47 C 73 35, 55 30, 43 34"
                fill="none"
                stroke="rgba(255,255,255,.16)"
                strokeWidth="8"
                strokeLinecap="round"
              />
              <path
                d="M18 58 C 11 38, 23 15, 45 16 C 72 17, 88 28, 85 48 C 82 70, 65 85, 42 80 C 23 76, 22 65, 34 58 C 48 50, 62 57, 67 47 C 73 35, 55 30, 43 34"
                fill="none"
                stroke="rgba(255,255,255,.45)"
                strokeWidth="1"
                strokeLinecap="round"
                strokeDasharray="2 4"
              />
            </svg>

            {cars.map((car) => (
              <button
                type="button"
                key={car.driver_number}
                className={`driver-marker ${activeDriver?.driver_number === car.driver_number ? 'active' : ''}`}
                style={{
                  '--x': `${car.x}%`,
                  '--y': `${car.y}%`,
                  '--team-color': car.team_color,
                }}
                onClick={() => setSelectedDriver(car.driver_number)}
                title={`${car.code} P${car.position}`}
              >
                <span>{car.code}</span>
              </button>
            ))}
          </div>
        </article>

        <aside className="race-side-panel">
          {activeDriver && (
            <article className="focus-driver" style={{ '--team-color': activeDriver.team_color }}>
              <div className="driver-photo-wrap">
                {activeDriver.headshot_url ? (
                  <img src={activeDriver.headshot_url} alt={activeDriver.name} />
                ) : (
                  <span>{activeDriver.code}</span>
                )}
              </div>
              <div>
                <span className="panel-label">Selected driver</span>
                <h2>{activeDriver.name}</h2>
                <p>{activeDriver.team_name}</p>
              </div>
              <div className="focus-stats">
                <strong>P{activeDriver.position}</strong>
                <span>{formatDelta(activeDriver.gap_to_leader)}</span>
                <span>{Math.round(activeDriver.speed || 0)} km/h</span>
              </div>
            </article>
          )}

          <div className="weather-grid">
            <div><span>Air</span><strong>{formatWeather(weather.air_temperature, 'C')}</strong></div>
            <div><span>Track</span><strong>{formatWeather(weather.track_temperature, 'C')}</strong></div>
            <div><span>Humidity</span><strong>{formatWeather(weather.humidity, '%')}</strong></div>
            <div><span>Wind</span><strong>{formatWeather(weather.wind_speed, ' m/s')}</strong></div>
          </div>

          <div className="race-messages">
            <h3>Race control</h3>
            {raceControl.slice(0, 5).map((message, index) => (
              <div key={`${message.date}-${index}`} className="message-row">
                <span>{message.flag || message.category || 'INFO'}</span>
                <p>{message.message || 'Session update'}</p>
              </div>
            ))}
            {raceControl.length === 0 && <p className="muted">No race-control messages in the latest packet.</p>}
          </div>
        </aside>
      </section>}

      {liveRace && <section className="section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Intervals and location</span>
            <h2>Continuous driver order</h2>
          </div>
        </div>
        <div className="live-timing-table">
          {cars.map((car, index) => (
            <button
              type="button"
              key={`${car.driver_number}-row`}
              className="timing-row"
              style={{ '--team-color': car.team_color, '--delay': `${index * 25}ms` }}
              onClick={() => setSelectedDriver(car.driver_number)}
            >
              <span className="rank">P{car.position}</span>
              <span className="driver-code">{car.code}</span>
              <span>{car.name}</span>
              <span>{formatDelta(car.interval)}</span>
              <span>{formatDelta(car.gap_to_leader)}</span>
              <span>{Math.round(car.speed || 0)} km/h</span>
              <span>{Math.round((car.throttle || 0) * 100)}% THR</span>
              <span>{car.drs ? 'DRS' : 'NO DRS'}</span>
            </button>
          ))}
        </div>
      </section>}
    </div>
  );
}
