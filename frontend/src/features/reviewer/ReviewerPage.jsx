import { useState } from 'react'
import { useSubmissions } from '../../hooks/useSubmissions.js'
import SubmissionList from '../../components/SubmissionList.jsx'
import ReviewRow from './ReviewRow.jsx'

const TABS = [
  { label: 'Pending', status: 'pending' },
  { label: 'Approved', status: 'approved' },
  { label: 'Rejected', status: 'rejected' },
  { label: 'All', status: '' },
]

export default function ReviewerPage() {
  const [status, setStatus] = useState('pending')
  const { data, loading, error, reload } = useSubmissions(status)

  return (
    <>
      <h2>Submissions</h2>
      <div className="switch">
        {TABS.map((t) => (
          <button
            key={t.label}
            className={status === t.status ? 'active' : ''}
            aria-pressed={status === t.status}
            onClick={() => setStatus(t.status)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <SubmissionList
        items={data}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyText="No submissions here."
        renderItem={(s) => <ReviewRow submission={s} onChanged={reload} />}
      />
    </>
  )
}
