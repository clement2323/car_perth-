'use client'

import { useState, useEffect } from 'react'
import type { ModelStat } from '@/types'
import { fetchStats } from '@/api'

export function useStats() {
  const [stats, setStats] = useState<ModelStat[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
      .then(data => { setStats(data); setError(null) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { stats, loading, error }
}
