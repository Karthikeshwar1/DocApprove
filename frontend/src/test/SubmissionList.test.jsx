import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import StatusBadge from '../components/StatusBadge.jsx'
import SubmissionList from '../components/SubmissionList.jsx'
import { ApiError } from '../api/client.js'

const base = { items: [], loading: false, error: null, onRetry: vi.fn(), emptyText: 'Nothing here.' }
const row = (s) => <span>{s.title}</span>

describe('StatusBadge', () => {
  it.each(['pending', 'approved', 'rejected'])('renders %s', (status) => {
    render(<StatusBadge status={status} />)
    expect(screen.getByText(status)).toHaveClass(`badge-${status}`)
  })
})

describe('SubmissionList', () => {
  it('renders items', () => {
    render(<SubmissionList {...base} items={[{ id: 1, title: 'A' }, { id: 2, title: 'B' }]} renderItem={row} />)
    expect(screen.getByText('A')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
  })

  it('shows the empty state', () => {
    render(<SubmissionList {...base} renderItem={row} />)
    expect(screen.getByText('Nothing here.')).toBeInTheDocument()
  })

  it('shows the loading state', () => {
    render(<SubmissionList {...base} loading renderItem={row} />)
    expect(screen.getByText(/Loading/, { selector: 'p' })).toBeInTheDocument()
  })

  it('shows an error banner with Retry', async () => {
    const onRetry = vi.fn()
    render(<SubmissionList {...base} onRetry={onRetry} error={new ApiError(0, 'network_error', 'Offline')} renderItem={row} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Offline')
    await userEvent.click(screen.getByRole('button', { name: 'Retry' }))
    expect(onRetry).toHaveBeenCalledOnce()
  })
})
