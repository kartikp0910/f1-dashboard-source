import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchJson, getNextRace, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function Predict({ apiBase = 'http://localhost:8000' }) {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    circuit_id: '',
    season: new Date().getFullYear(),
    round: 1,
    weather_condition: 'dry',
    safety_car_probability: 0.3,
  });

  const fetchRaces = useCallback(() => fetchJson(`${apiBase}/races?season=current`), [apiBase]);
  const { data, loading: racesLoading, updatedAt } = useLiveResource(fetchRaces, [apiBase], {
    intervalMs: 90000,
  });
  const races = data || [];

  const nextRace = useMemo(() => getNextRace(races), [races]);

  useEffect(() => {
    if (!nextRace || formData.circuit_id) return;
    setFormData((prev) => ({
      ...prev,
      circuit_id: nextRace.circuit_id,
      season: Number(nextRace.season),
      round: Number(nextRace.round),
    }));
  }, [nextRace, formData.circuit_id]);

  const selectedRace = races.find((race) => Number(race.round) === Number(formData.round)) || nextRace;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: ['season', 'round'].includes(name) ? Number(value) : value,
    }));
  };

  const handleRaceChange = (e) => {
    const race = races.find((item) => String(item.round) === e.target.value);
    if (!race) return;
    setFormData((prev) => ({
      ...prev,
      circuit_id: race.circuit_id,
      season: Number(race.season),
      round: Number(race.round),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await fetchJson(`${apiBase}/predictions/winner`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      setPredictions(data);
    } catch (error) {
      setError(error.message || 'Could not fetch live prediction data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page predict-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Live-fed model</span>
          <h1>Race winner predictions</h1>
        </div>
        <div className="live-strip compact">
          <span className="live-pill">Inputs live</span>
          <span>{updatedAt ? updatedAt.toLocaleTimeString() : 'Syncing'}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-group span-2">
          <label htmlFor="round">Race</label>
          <select id="round" name="round" value={String(formData.round)} onChange={handleRaceChange} disabled={racesLoading || races.length === 0}>
            {races.map((race) => (
              <option key={`${race.season}-${race.round}`} value={race.round}>
                Round {race.round} - {race.race_name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="weather_condition">Weather</label>
          <select id="weather_condition" name="weather_condition" value={formData.weather_condition} onChange={handleInputChange}>
            <option value="dry">Dry</option>
            <option value="wet">Wet</option>
            <option value="mixed">Mixed</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="safety_car_probability">Safety car probability</label>
          <input
            type="range"
            id="safety_car_probability"
            name="safety_car_probability"
            min="0"
            max="1"
            step="0.05"
            value={formData.safety_car_probability}
            onChange={(e) => setFormData((prev) => ({ ...prev, safety_car_probability: Number(e.target.value) }))}
          />
          <span className="range-value">{Math.round(formData.safety_car_probability * 100)}%</span>
        </div>

        <div className="form-summary">
          <span>{selectedRace?.circuit_name || formData.circuit_id || 'Circuit pending'}</span>
          <strong>{selectedRace?.race_name || `Round ${formData.round}`}</strong>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading || !formData.circuit_id}>
          {loading ? 'Running model...' : 'Run live prediction'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {predictions && (
        <section className="predictions-results">
          <div className="prediction-hero">
            <div>
              <span className="eyebrow">{predictions.weather_condition} conditions</span>
              <h2>{predictions.race_name}</h2>
            </div>
            <div className="confidence-ring" style={{ '--confidence': `${predictions.model_confidence * 100}%` }}>
              <strong>{Math.round(predictions.model_confidence * 100)}%</strong>
              <span>confidence</span>
            </div>
          </div>

          <div className="insights">
            <h3>Key insights</h3>
            <ul>
              {predictions.key_insights.map((insight) => (
                <li key={insight}>{insight}</li>
              ))}
            </ul>
          </div>

          <div className="prediction-list">
            {predictions.predictions.slice(0, 10).map((pred, index) => (
              <article key={pred.driver_id} className="prediction-row" style={{ '--team-color': pred.constructor_color || '#e10600', '--delay': `${index * 45}ms` }}>
                <div className="rank">#{pred.predicted_position}</div>
                <div>
                  <h3>{pred.driver_name}</h3>
                  <p>{pred.constructor_name}</p>
                </div>
                <div className="probability-bars">
                  <label>Win <span>{(pred.win_probability * 100).toFixed(1)}%</span></label>
                  <div className="progress-track"><span style={{ width: `${pred.win_probability * 100}%` }} /></div>
                  <label>Podium <span>{(pred.podium_probability * 100).toFixed(1)}%</span></label>
                  <div className="progress-track podium"><span style={{ width: `${pred.podium_probability * 100}%` }} /></div>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
