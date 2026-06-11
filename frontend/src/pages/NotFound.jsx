/**
 * 404 Not Found page
 */
export default function NotFound() {
  return (
    <div className="page not-found">
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <button onClick={() => window.location.hash = 'home'} className="btn btn-primary">
        Go Home
      </button>
    </div>
  );
}
