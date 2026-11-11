import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReviewRow from '../features/reviewer/ReviewRow.jsx'
import { decideSubmission } from '../api/submissions.js'
import { ApiError } from '../api/client.js'

vi.mock('../api/submissions.js')

const pending = {
  id: 7, title: 'Budget', content: 'Q3 numbers', file_name: null, status: 'pending',
  submitted_by: 'alice', created_at: '2026-01-01T10:00:00Z', decided_by: null, decided_at: null,
}

beforeEach(() => vi.resetAllMocks())

describe('ReviewRow', () => {
  it('approves and refreshes the list', async () => {
    decideSubmission.mockResolvedValue({ ...pending, status: 'approved' })
    const onChanged = vi.fn()
    render(<ReviewRow submission={pending} onChanged={onChanged} />)
    await userEvent.click(screen.getByRole('button', { name: /approve/i }))

    expect(decideSubmission).toHaveBeenCalledWith(7, 'approved')
    expect(onChanged).toHaveBeenCalledOnce()
  })

  it('rejects via the Reject button', async () => {
    decideSubmission.mockResolvedValue({ ...pending, status: 'rejected' })
    render(<ReviewRow submission={pending} onChanged={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /reject/i }))
    expect(decideSubmission).toHaveBeenCalledWith(7, 'rejected')
  })

  it('shows the 409 message inline and refreshes the list', async () => {
    decideSubmission.mockRejectedValue(new ApiError(409, 'invalid_transition', 'Already approved.'))
    const onChanged = vi.fn()
    render(<ReviewRow submission={pending} onChanged={onChanged} />)
    await userEvent.click(screen.getByRole('button', { name: /reject/i }))

    expect(await screen.findByText('Already approved.')).toBeInTheDocument()
    expect(onChanged).toHaveBeenCalledOnce()
  })

  it('disables both buttons while a decision is in flight', async () => {
    decideSubmission.mockReturnValue(new Promise(() => {})) // never resolves
    render(<ReviewRow submission={pending} onChanged={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /approve/i }))

    expect(screen.getByRole('button', { name: /approve/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /reject/i })).toBeDisabled()
  })

  it('shows no buttons for a decided submission', () => {
    render(<ReviewRow submission={{ ...pending, status: 'approved' }} onChanged={vi.fn()} />)
    expect(screen.queryByRole('button', { name: /approve/i })).toBeNull()
  })
})
