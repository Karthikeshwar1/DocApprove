import { useCallback, useEffect, useState } from 'react'
import { listSubmissions } from '../api/submissions.js'

// Loads submissions (optionally filtered by status) and exposes reload().
export function useSubmissions(status) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await listSubmissions(status))
    } catch (e) {
      setError(e)
    } finally {
      setLoading(false)
    }
  }, [status])

  useEffect(() => { reload() }, [reload])

  return { data, loading, error, reload }
}
