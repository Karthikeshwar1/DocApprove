export default function ErrorBanner({ error, onRetry }) {
  return (
    <div className="banner" role="alert">
      <span>{error.message}</span>
      {onRetry && <button onClick={onRetry}>Retry</button>}
    </div>
  )
}
