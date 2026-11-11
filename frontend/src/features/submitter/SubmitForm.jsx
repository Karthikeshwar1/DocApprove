import { useState } from 'react'
import { createSubmission } from '../../api/submissions.js'
import Spinner from '../../components/Spinner.jsx'

const MAX_FILE_BYTES = 5 * 1024 * 1024
const ALLOWED = ['pdf', 'txt', 'md', 'docx']

// Client-side checks mirror the server's rules; the server stays authoritative.
function validate({ title, mode, content, file }) {
  const errors = {}
  if (!title.trim()) errors.title = 'Title is required.'
  if (mode === 'text' && !content.trim()) errors.content = 'Content is required.'
  if (mode === 'file') {
    if (!file) errors.file = 'Choose a file.'
    else if (!ALLOWED.includes(file.name.split('.').pop().toLowerCase()))
      errors.file = `Allowed types: ${ALLOWED.join(', ')}.`
    else if (file.size > MAX_FILE_BYTES) errors.file = 'File too large (max 5 MB).'
  }
  return errors
}

export default function SubmitForm({ onCreated }) {
  const [title, setTitle] = useState('')
  const [mode, setMode] = useState('text') // 'text' | 'file'
  const [content, setContent] = useState('')
  const [file, setFile] = useState(null)
  const [errors, setErrors] = useState({}) // per-field messages
  const [formError, setFormError] = useState('') // non-field error
  const [busy, setBusy] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    const found = validate({ title, mode, content, file })
    setErrors(found)
    setFormError('')
    if (Object.keys(found).length) return

    let payload = { title, content }
    if (mode === 'file') {
      payload = new FormData()
      payload.append('title', title)
      payload.append('file', file)
    }

    setBusy(true)
    try {
      await createSubmission(payload)
      setTitle('')
      setContent('')
      setFile(null)
      onCreated()
    } catch (err) {
      if (err.code === 'validation_error') {
        // details is {field: [messages]}; show the first message per field.
        const fieldErrors = {}
        for (const [field, msgs] of Object.entries(err.details || {})) fieldErrors[field] = msgs[0]
        setErrors(fieldErrors)
      } else {
        setFormError(err.message)
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="card" noValidate>
      <label>Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
      </label>
      {errors.title && <p className="field-error">{errors.title}</p>}

      <div className="switch">
        <button type="button" className={mode === 'text' ? 'active' : ''} onClick={() => setMode('text')}>
          Write text
        </button>
        <button type="button" className={mode === 'file' ? 'active' : ''} onClick={() => setMode('file')}>
          Upload file
        </button>
      </div>

      {mode === 'text' ? (
        <label>Content
          <textarea rows={5} value={content} onChange={(e) => setContent(e.target.value)} />
        </label>
      ) : (
        <label>File (pdf, txt, md, docx; max 5 MB)
          <input type="file" onChange={(e) => setFile(e.target.files[0] || null)} />
        </label>
      )}
      {errors.content && <p className="field-error">{errors.content}</p>}
      {errors.file && <p className="field-error">{errors.file}</p>}
      {errors.non_field_errors && <p className="field-error">{errors.non_field_errors}</p>}
      {formError && <p className="field-error">{formError}</p>}

      <button type="submit" disabled={busy}>{busy && <Spinner />} Submit</button>
    </form>
  )
}
