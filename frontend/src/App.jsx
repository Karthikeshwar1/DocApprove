import { useAuth } from './auth/AuthContext.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SubmitterPage from './features/submitter/SubmitterPage.jsx'
import ReviewerPage from './features/reviewer/ReviewerPage.jsx'

export default function App() {
  const { user, logout } = useAuth()
  if (!user) return <LoginPage />

  return (
    <div className="container">
      <header className="topbar">
        <h1>Document Approval</h1>
        <span>
          {user.username} ({user.role}){' '}
          <button onClick={logout}>Log out</button>
        </span>
      </header>
      {user.role === 'reviewer' ? <ReviewerPage /> : <SubmitterPage />}
    </div>
  )
}
