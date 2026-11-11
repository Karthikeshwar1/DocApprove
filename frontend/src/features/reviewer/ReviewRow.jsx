import { useState } from 'react'
import { decideSubmission } from '../../api/submissions.js'
import StatusBadge from '../../components/StatusBadge.jsx'
import SubmissionBody from '../../components/SubmissionBody.jsx'
import Spinner from '../../components/Spinner.jsx'

export default function ReviewRow({ submission, onChanged }) {
  const [busy, setBusy] = useState('') // which decision is in flight
  const [error, setError] = useState('')

  const decide = async (status) => {
    setBusy(status)
    setError('')
    try {
      await decideSubmission(submission.id, status)
      onChanged()
    } catch (e) {
      setError(e.message) // e.g. 409 "already decided"
      if (e.status === 409) onChanged() // list is stale, refresh it
    } finally {
      setBusy('')
    }
  }

  return (
    <>
      <div className="row-head">
        <strong>{submission.title}</strong>
        <StatusBadge status={submission.status} />
      </div>
      <div className="muted">
        By {submission.submitted_by} on {new Date(submission.created_at).toLocaleString()}
      </div>
      <SubmissionBody submission={submission} />
      {submission.status === 'pending' && (
        <div className="actions">
          <button disabled={!!busy} onClick={() => decide('approved')}>
            {busy === 'approved' && <Spinner />} Approve
          </button>
          <button disabled={!!busy} onClick={() => decide('rejected')}>
            {busy === 'rejected' && <Spinner />} Reject
          </button>
        </div>
      )}
      {error && <p className="field-error">{error}</p>}
    </>
  )
}
