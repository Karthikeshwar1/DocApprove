import { createContext, useContext, useState } from 'react'
import { login as loginRequest } from '../api/auth.js'
import { setToken, setOnUnauthorized } from '../api/client.js'

const AuthContext = createContext(null)
const KEY = 'session'

// localStorage can throw (private mode, blocked), so never trust it blindly.
function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(KEY))
  } catch {
    return null
  }
}
function saveSession(session) {
  try {
    if (session) localStorage.setItem(KEY, JSON.stringify(session))
    else localStorage.removeItem(KEY)
  } catch {
    /* session just won't survive a reload */
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const s = loadSession()
    setToken(s?.token ?? null)
    return s
  })

  const update = (s) => {
    setToken(s?.token ?? null)
    saveSession(s)
    setSession(s)
  }
  const logout = () => update(null)
  setOnUnauthorized(logout) // any 401 from the API drops us back to login

  const login = async (username, password) => {
    const { token, user } = await loginRequest(username, password)
    update({ token, user })
  }

  return (
    <AuthContext.Provider value={{ user: session?.user ?? null, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
