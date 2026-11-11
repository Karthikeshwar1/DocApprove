import { useState } from 'react'
import { useAuth } from '../auth/AuthContext.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import Spinner from '../components/Spinner.jsx'

export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login(username, password)
    } catch (err) {
      setError(err)
      setBusy(false)
    }
  }

  return (
    <div className="container narrow">
      <h1>Document Approval</h1>
      <form onSubmit={onSubmit} className="card">
        <label>Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
        </label>
        <label>Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <ErrorBanner error={error} />}
        <button type="submit" disabled={busy}>{busy && <Spinner />} Log in</button>
      </form>
      <p className="muted">
        Demo users: alice, bob (submitters), rita (reviewer). Password: demo-pass
      </p>
    </div>
  )
}
