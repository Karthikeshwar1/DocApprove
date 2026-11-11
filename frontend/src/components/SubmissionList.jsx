import Spinner from './Spinner.jsx'
import ErrorBanner from './ErrorBanner.jsx'

// Handles loading / error / empty states; renderItem draws each row.
export default function SubmissionList({ items, loading, error, onRetry, emptyText, renderItem }) {
  if (error) return <ErrorBanner error={error} onRetry={onRetry} />
  if (loading) return <p className="state"><Spinner /> Loading...</p>
  if (items.length === 0) return <p className="state">{emptyText}</p>
  return <ul className="list">{items.map((s) => <li key={s.id}>{renderItem(s)}</li>)}</ul>
}
