import { describe, it, expect, vi, beforeEach } from 'vitest'
import { request, setToken, setOnUnauthorized, ApiError } from '../api/client.js'

const jsonResponse = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

beforeEach(() => {
  setToken('abc')
  setOnUnauthorized(() => {})
  vi.stubGlobal('fetch', vi.fn())
})

describe('api client', () => {
  it('attaches the token and sends JSON bodies', async () => {
    fetch.mockResolvedValue(jsonResponse(200, { ok: true }))
    await request('/x/', { method: 'POST', body: { a: 1 } })

    const [url, opts] = fetch.mock.calls[0]
    expect(url).toBe('/api/x/')
    expect(opts.headers.Authorization).toBe('Token abc')
    expect(opts.headers['Content-Type']).toBe('application/json')
    expect(opts.body).toBe('{"a":1}')
  })

  it('does not set Content-Type for FormData', async () => {
    fetch.mockResolvedValue(jsonResponse(201, {}))
    await request('/x/', { method: 'POST', body: new FormData() })
    expect(fetch.mock.calls[0][1].headers['Content-Type']).toBeUndefined()
  })

  it('builds an ApiError from the error envelope', async () => {
    fetch.mockResolvedValue(
      jsonResponse(400, { error: { code: 'validation_error', message: 'Bad', details: { title: ['Required'] } } }),
    )
    const err = await request('/x/').catch((e) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err).toMatchObject({ status: 400, code: 'validation_error', message: 'Bad', details: { title: ['Required'] } })
  })

  it('turns a network failure into network_error', async () => {
    fetch.mockRejectedValue(new TypeError('Failed to fetch'))
    const err = await request('/x/').catch((e) => e)
    expect(err.code).toBe('network_error')
  })

  it('calls the unauthorized handler on 401', async () => {
    const handler = vi.fn()
    setOnUnauthorized(handler)
    fetch.mockResolvedValue(jsonResponse(401, { error: { code: 'not_authenticated', message: 'No' } }))
    await request('/x/').catch(() => {})
    expect(handler).toHaveBeenCalledOnce()
  })
})
