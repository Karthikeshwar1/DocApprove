import { useState } from 'react'
import { downloadFile } from '../api/submissions.js'

export default function FileLink({ submission }) {
  const [error, setError] = useState('')

  const onClick = async () => {
    setError('')
    try {
      await downloadFile(submission)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <button className="link" onClick={onClick}>Download {submission.file_name}</button>
      {error && <span className="field-error"> {error}</span>}
    </>
  )
}
