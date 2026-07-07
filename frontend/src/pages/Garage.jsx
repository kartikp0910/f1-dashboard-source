import { useCallback, useMemo, useState } from 'react';
import { fetchJson, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Garage({ apiBase = 'http://localhost:8000' }) {
  const [selectedId, setSelectedId] = useState(null);
  const [selectedUpgrade, setSelectedUpgrade] = useState(0);
  const fetchConstructors = useCallback(() => fetchJson(`${apiBase}/constructors/specs?season=current`), [apiBase]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchConstructors, [apiBase], {
    intervalMs: 90000,
  });
  const constructors = data || [];
  const selectedTeam = useMemo(
    () => constructors.find((constructor) => constructor.constructor_id === selectedId) || constructors[0],
    [constructors, selectedId],
  );
  const upgrades = selectedTeam?.upgrade_timeline || [];
  const activeUpgrade = upgrades[selectedUpgrade] || upgrades[0];

  if (loading) {
    return <div className="loading"><span className="spinner" />Opening constructor garage...</div>;
  }

  return (
    <div className="page garage-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Constructor garage</span>
          <h1>Cars, specs, and upgrades</h1>
        </div>
        <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="live-strip">
        <span className="live-pill">Tech tracker</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Syncing constructor data'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <section className="garage-layout">
        <aside className="constructor-list">
          {constructors.map((constructor, index) => (
            <button
              key={constructor.constructor_id}
              type="button"
              className={`constructor-tab ${selectedTeam?.constructor_id === constructor.constructor_id ? 'active' : ''}`}
              style={{ '--team-color': constructor.color, '--delay': `${index * 30}ms` }}
              onClick={() => {
                setSelectedId(constructor.constructor_id);
                setSelectedUpgrade(0);
              }}
            >
              <span>{constructor.name}</span>
              <strong>{Math.round(constructor.points)} pts</strong>
            </button>
          ))}
        </aside>

        {selectedTeam && (
          <article className="garage-stage" style={{ '--team-color': selectedTeam.color }}>
            <div className="garage-header">
              <div>
                <span className="panel-label">Selected constructor</span>
                <h2>{selectedTeam.name}</h2>
                <p>{selectedTeam.drivers?.join(' / ') || 'Drivers pending'}</p>
              </div>
              <div className="focus-stats">
                <strong>{Math.round(selectedTeam.points)} pts</strong>
                <span>{selectedTeam.wins} wins</span>
              </div>
            </div>

            <div className="car-viewer" aria-label={`${selectedTeam.name} interactive car model`}>
              <div className="car-model">
                <span className={`hotspot hotspot-front ${activeUpgrade?.area === 'Front wing' ? 'active' : ''}`} />
                <span className={`hotspot hotspot-floor ${activeUpgrade?.area === 'Floor edge' ? 'active' : ''}`} />
                <span className={`hotspot hotspot-sidepod ${activeUpgrade?.area === 'Sidepod bodywork' ? 'active' : ''}`} />
                <span className={`hotspot hotspot-rear ${activeUpgrade?.area === 'Rear wing' ? 'active' : ''}`} />
                <span className={`hotspot hotspot-diffuser ${activeUpgrade?.area === 'Diffuser' ? 'active' : ''}`} />
                <div className="car-nose" />
                <div className="car-body" />
                <div className="car-cockpit" />
                <div className="car-sidepod left" />
                <div className="car-sidepod right" />
                <div className="car-wing front" />
                <div className="car-wing rear" />
                <div className="car-wheel front-left" />
                <div className="car-wheel front-right" />
                <div className="car-wheel rear-left" />
                <div className="car-wheel rear-right" />
              </div>
            </div>

            <div className="upgrade-panel">
              <div>
                <span className="eyebrow">{activeUpgrade?.race || 'Upgrade'}</span>
                <h3>{activeUpgrade?.area || 'Car package'} - {activeUpgrade?.version || 'Current'}</h3>
                <p>{activeUpgrade?.impact || selectedTeam.aero_focus}</p>
              </div>
              <div className="upgrade-buttons">
                {upgrades.map((upgrade, index) => (
                  <button
                    type="button"
                    key={`${upgrade.area}-${upgrade.version}`}
                    className={index === selectedUpgrade ? 'active' : ''}
                    onClick={() => setSelectedUpgrade(index)}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
            </div>

            <div className="spec-grid">
              <div><span>Power unit</span><strong>{selectedTeam.power_unit}</strong></div>
              <div><span>Chassis</span><strong>{selectedTeam.chassis}</strong></div>
              <div><span>Tyres</span><strong>{selectedTeam.tyres}</strong></div>
              <div><span>Brakes</span><strong>{selectedTeam.brakes}</strong></div>
              <div><span>Aero focus</span><strong>{selectedTeam.aero_focus}</strong></div>
              <div><span>Risk</span><strong>{selectedTeam.risk}</strong></div>
            </div>
          </article>
        )}
      </section>
    </div>
  );
}
