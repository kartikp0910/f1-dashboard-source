import { useCallback } from 'react';
import { fetchJson, useLiveResource } from '../lib/liveData';
import '../styles/pages.css';

export default function NewsHub({ apiBase = 'http://localhost:8000' }) {
  const fetchNews = useCallback(() => fetchJson(`${apiBase}/news`), [apiBase]);
  const { data, loading, error, updatedAt, refreshing, refresh } = useLiveResource(fetchNews, [apiBase], {
    intervalMs: 180000,
  });
  const updates = data || [];

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading F1 updates...</div>;
  }

  return (
    <div className="page news-page">
      <div className="page-header">
        <div>
          <span className="eyebrow">Paddock feed</span>
          <h1>News and updates</h1>
        </div>
        <button type="button" className="btn btn-secondary" onClick={refresh} disabled={refreshing}>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="live-strip">
        <span className="live-pill">Feed</span>
        <span>{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Syncing updates'}</span>
        {error && <span className="muted">{error}</span>}
      </div>

      <section className="news-grid">
        {updates.map((item, index) => (
          <article
            key={item.id}
            className="news-card"
            style={{ '--team-color': item.accent || '#E10600', '--delay': `${index * 55}ms` }}
          >
            <div className="news-meta">
              <span>{item.type}</span>
              <span>{item.source}</span>
            </div>
            <h2>{item.title}</h2>
            <p>{item.summary}</p>
            {item.url?.startsWith('#') ? (
              <button type="button" className="text-button" onClick={() => { window.location.hash = item.url.slice(1); }}>
                Open in dashboard
              </button>
            ) : (
              <a className="text-link" href={item.url} target="_blank" rel="noreferrer">
                Open source
              </a>
            )}
          </article>
        ))}
      </section>
    </div>
  );
}
