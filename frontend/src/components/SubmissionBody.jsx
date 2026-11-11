import FileLink from './FileLink.jsx'

const PREVIEW_CHARS = 200

// Text preview, or a download link when the submission is a file.
export default function SubmissionBody({ submission }) {
  if (submission.file_name) return <FileLink submission={submission} />
  const { content } = submission
  const text = content.length > PREVIEW_CHARS ? content.slice(0, PREVIEW_CHARS) + '...' : content
  return <p className="preview">{text}</p>
}
