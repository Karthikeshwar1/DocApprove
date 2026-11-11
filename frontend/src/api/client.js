// Single place that talks to the backend. Everything else goes through request().
const BASE = '/api'

export class ApiError extends Error {
  constructor(status, code, message, details = {}) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

// Token + 401 callback are set by AuthContext so this module stays React-free.
let token = null
let onUnauthorized = () => {}
export const setToken = (t) => { token = t }
export const setOnUnauthorized = (fn) => { onUnauthorized = fn }

// body: plain object (sent as JSON) or FormData (sent as multipart).
// Pass raw: true to get the Response back (used for file downloads).
export async function request(path, { method = 'GET', body, raw = false } = {}) {
  const headers = {}
  if (token) headers.Authorization = `Token ${token}`
  if (body && !(body instanceof FormData)) headers['Content-Type'] = 'application/json'

  let res
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: body instanceof FormData || body === undefined ? body : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'network_error', 'Cannot reach the server. Check your connection.')
  }

  if (!res.ok) {
    // Backend always returns {"error": {code, message, details}}.
    const data = await res.json().catch(() => ({}))
    const err = data.error || {}
    if (res.status === 401 && token) onUnauthorized()
    throw new ApiError(res.status, err.code || 'unknown_error', err.message || 'Something went wrong.', err.details)
  }
  return raw ? res : res.json()
}
