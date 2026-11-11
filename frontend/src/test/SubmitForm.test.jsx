import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SubmitForm from '../features/submitter/SubmitForm.jsx'
import { createSubmission } from '../api/submissions.js'
import { ApiError } from '../api/client.js'

vi.mock('../api/submissions.js')

beforeEach(() => vi.resetAllMocks())

describe('SubmitForm', () => {
  it('shows client-side errors and does not call the API', async () => {
    render(<SubmitForm onCreated={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /submit/i }))

    expect(screen.getByText('Title is required.')).toBeInTheDocument()
    expect(screen.getByText('Content is required.')).toBeInTheDocument()
    expect(createSubmission).not.toHaveBeenCalled()
  })

  it('rejects a disallowed file type client-side', async () => {
    render(<SubmitForm onCreated={vi.fn()} />)
    await userEvent.type(screen.getByLabelText('Title'), 'Doc')
    await userEvent.click(screen.getByRole('button', { name: 'Upload file' }))
    // applyAccept off: userEvent would otherwise filter by the accept attribute
    await userEvent.upload(screen.getByLabelText(/File/), new File(['x'], 'evil.exe'), { applyAccept: false })
    await userEvent.click(screen.getByRole('button', { name: /submit/i }))

    expect(screen.getByText(/Allowed types/)).toBeInTheDocument()
    expect(createSubmission).not.toHaveBeenCalled()
  })

  it('shows per-field errors returned by the server', async () => {
    createSubmission.mockRejectedValue(
      new ApiError(400, 'validation_error', 'Invalid', { title: ['Title is too long.'] }),
    )
    render(<SubmitForm onCreated={vi.fn()} />)
    await userEvent.type(screen.getByLabelText('Title'), 'Doc')
    await userEvent.type(screen.getByLabelText('Content'), 'Hello')
    await userEvent.click(screen.getByRole('button', { name: /submit/i }))

    expect(await screen.findByText('Title is too long.')).toBeInTheDocument()
  })

  it('calls onCreated on success', async () => {
    createSubmission.mockResolvedValue({ id: 1 })
    const onCreated = vi.fn()
    render(<SubmitForm onCreated={onCreated} />)
    await userEvent.type(screen.getByLabelText('Title'), 'Doc')
    await userEvent.type(screen.getByLabelText('Content'), 'Hello')
    await userEvent.click(screen.getByRole('button', { name: /submit/i }))

    expect(createSubmission).toHaveBeenCalledWith({ title: 'Doc', content: 'Hello' })
    expect(onCreated).toHaveBeenCalledOnce()
  })
})
