import { useEffect, useState } from 'react';
import Layout from './components/Layout';
import Home from './pages/Home';
import Standings from './pages/Standings';
import RaceDetail from './pages/RaceDetail';
import Calendar from './pages/Calendar';
import Predict from './pages/Predict';
import Telemetry from './pages/Telemetry';
import RaceCenter from './pages/RaceCenter';
import DriverProfiles from './pages/DriverProfiles';
import Garage from './pages/Garage';
import NewsHub from './pages/NewsHub';
import NotFound from './pages/NotFound';
import './styles/app.css';

const API_BASE_URL = '/api';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [params, setParams] = useState({});
  const [apiError, setApiError] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      const [page, ...rest] = hash.split('/');
      setCurrentPage(page || 'home');
      setParams(Object.fromEntries(rest.map((p) => p.split('='))));
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home apiBase={API_BASE_URL} />;
      case 'standings':
        return <Standings apiBase={API_BASE_URL} />;
      case 'race-detail':
        return <RaceDetail raceId={params.id} apiBase={API_BASE_URL} />;
      case 'calendar':
        return <Calendar apiBase={API_BASE_URL} />;
      case 'race-center':
        return <RaceCenter apiBase={API_BASE_URL} />;
      case 'predict':
        return <Predict apiBase={API_BASE_URL} />;
      case 'telemetry':
        return <Telemetry apiBase={API_BASE_URL} />;
      case 'drivers':
        return <DriverProfiles apiBase={API_BASE_URL} />;
      case 'garage':
        return <Garage apiBase={API_BASE_URL} />;
      case 'news':
        return <NewsHub apiBase={API_BASE_URL} />;
      default:
        return <NotFound />;
    }
  };

  return (
    <Layout currentPage={currentPage} onNavigate={(page) => { window.location.hash = page; }}>
      {!isOnline && (
        <div className="offline-banner">
          You are offline. Live panels will reconnect automatically.
        </div>
      )}
      {apiError && (
        <div className="error-banner">
          {apiError}
          <button type="button" onClick={() => setApiError(null)}>Dismiss</button>
        </div>
      )}
      {renderPage()}
    </Layout>
  );
}

export default App;
