import { request } from './client.js'

export const listSubmissions = (status) =>
  request(status ? `/submissions/?status=${status}` : '/submissions/')

// data is FormData when a file is attached, otherwise a plain {title, content} object.
export const createSubmission = (data) => request('/submissions/', { method: 'POST', body: data })

export const decideSubmission = (id, status) =>
  request(`/submissions/${id}/status/`, { method: 'PATCH', body: { status } })

// The file endpoint needs the auth header, so fetch a blob and click a temporary link.
export async function downloadFile(submission) {
  const res = await request(`/submissions/${submission.id}/file/`, { raw: true })
  const url = URL.createObjectURL(await res.blob())
  const a = document.createElement('a')
  a.href = url
  a.download = submission.file_name
  a.click()
  URL.revokeObjectURL(url)
}
