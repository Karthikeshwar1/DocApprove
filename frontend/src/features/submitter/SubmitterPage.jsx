import { useSubmissions } from '../../hooks/useSubmissions.js'
import SubmissionList from '../../components/SubmissionList.jsx'
import SubmissionBody from '../../components/SubmissionBody.jsx'
import StatusBadge from '../../components/StatusBadge.jsx'
import SubmitForm from './SubmitForm.jsx'
import { formatDate } from '../../utils/format.js'

export default function SubmitterPage() {
  const { data, loading, error, reload } = useSubmissions()

  return (
    <>
      <h2>Submit a document</h2>
      <SubmitForm onCreated={reload} />
      <h2>My submissions</h2>
      <SubmissionList
        items={data}
        loading={loading}
        error={error}
        onRetry={reload}
        emptyText="You have not submitted anything yet."
        renderItem={(s) => (
          <>
            <div className="row-head">
              <strong>{s.title}</strong>
              <StatusBadge status={s.status} />
            </div>
            <div className="muted">Submitted {formatDate(s.created_at)}</div>
            <SubmissionBody submission={s} />
          </>
        )}
      />
    </>
  )
}
